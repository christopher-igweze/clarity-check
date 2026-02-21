"""Build orchestration state store with durable snapshot support."""

from __future__ import annotations

import asyncio
from collections import defaultdict
import json
import logging
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from config import settings
from models.builds import (
    BuildCheckpoint,
    BuildCreateRequest,
    BuildEvent,
    BuildRun,
    BuildRunSummary,
    BuildStatus,
    BuildStatusTransition,
    DebtItem,
    DagNode,
    GateDecision,
    GateDecisionStatus,
    GateType,
    PolicyViolation,
    ReplanAction,
    ReplanDecision,
    ReplanSuggestion,
    TaskRun,
    TaskStatus,
    utc_now,
)
from orchestration.scheduler import compute_dag_levels
from orchestration.telemetry import emit_orchestration_event
from services.control_plane_state import load_state_snapshot, save_state_snapshot

logger = logging.getLogger(__name__)


def _autonomous_default_dag() -> list[DagNode]:
    return [
        DagNode(node_id="scanner", title="Static scan", agent="scanner", depends_on=[]),
        DagNode(
            node_id="builder",
            title="Dynamic probe",
            agent="builder",
            depends_on=["scanner"],
            gate=GateType.test,
        ),
        DagNode(
            node_id="security",
            title="Security review",
            agent="security",
            depends_on=["builder"],
            gate=GateType.policy,
        ),
        DagNode(
            node_id="planner",
            title="Remediation plan",
            agent="planner",
            depends_on=["security"],
            gate=GateType.merge,
        ),
    ]


def _deterministic_default_dag() -> list[DagNode]:
    return [
        DagNode(node_id="deterministic-scan", title="Deterministic scan", agent="scanner", depends_on=[]),
        DagNode(
            node_id="deterministic-summary",
            title="Deterministic summary",
            agent="planner",
            depends_on=["deterministic-scan"],
        ),
    ]


def _resolve_default_dag(metadata: dict[str, Any]) -> tuple[list[DagNode], str]:
    raw_mode = str(metadata.get("scan_mode") or "autonomous").strip().lower()
    if raw_mode in {"deterministic", "tier1", "free"}:
        return _deterministic_default_dag(), "deterministic"
    return _autonomous_default_dag(), "autonomous"


_VALID_STATUS_TRANSITIONS: dict[BuildStatus, set[BuildStatus]] = {
    BuildStatus.pending: {BuildStatus.running, BuildStatus.aborted},
    BuildStatus.running: {
        BuildStatus.paused,
        BuildStatus.completed,
        BuildStatus.failed,
        BuildStatus.aborted,
    },
    BuildStatus.paused: {BuildStatus.running, BuildStatus.aborted},
    BuildStatus.failed: {BuildStatus.running, BuildStatus.aborted},
    BuildStatus.completed: set(),
    BuildStatus.aborted: set(),
}


class BuildStore:
    def __init__(self, *, state_path: str | None = None) -> None:
        self._lock = asyncio.Lock()
        self._builds: dict[UUID, BuildRun] = {}
        self._events: dict[UUID, list[BuildEvent]] = defaultdict(list)
        self._checkpoints: dict[UUID, list[BuildCheckpoint]] = defaultdict(list)
        resolved_path = state_path if state_path is not None else settings.build_store_state_path
        self._state_path = Path(resolved_path).expanduser() if resolved_path else None
        self._state_key = "build_store"
        self._load_state()

    async def create_build(self, *, user_id: str, request: BuildCreateRequest) -> BuildRun:
        async with self._lock:
            build_id = uuid4()
            now = utc_now()
            metadata = dict(request.metadata)
            if request.dag is not None:
                dag = request.dag
                scan_mode = str(metadata.get("scan_mode") or "custom").strip().lower()
            else:
                dag, scan_mode = _resolve_default_dag(metadata)
            metadata["scan_mode"] = scan_mode
            dag_levels = compute_dag_levels(dag)
            metadata["dag_levels"] = dag_levels
            metadata["level_cursor"] = 0
            build = BuildRun(
                build_id=build_id,
                created_by=user_id,
                repo_url=request.repo_url,
                objective=request.objective,
                status=BuildStatus.pending,
                created_at=now,
                updated_at=now,
                dag=dag,
                metadata=metadata,
            )
            self._builds[build_id] = build
            self._transition_build_status_unlocked(
                build=build,
                to_status=BuildStatus.running,
                reason="build_created",
                source="system",
            )
            self._append_event_unlocked(
                BuildEvent(
                    event_type="BUILD_STARTED",
                    build_id=build_id,
                    payload={
                        "repo_url": request.repo_url,
                        "objective": request.objective,
                        "scan_mode": metadata.get("scan_mode"),
                        "dag_nodes": [node.node_id for node in build.dag],
                    },
                )
            )
            if build.dag:
                level_zero_nodes = dag_levels[0] if dag_levels else []
                self._append_event_unlocked(
                    BuildEvent(
                        event_type="LEVEL_STARTED",
                        build_id=build_id,
                        payload={"level": 0, "nodes": level_zero_nodes},
                    )
                )
            self._append_checkpoint_unlocked(
                build_id=build_id,
                status=build.status,
                reason="build_created",
            )
            self._append_checkpoint_event_unlocked(
                build_id=build_id,
                reason="build_created",
                status=build.status,
            )
            emit_orchestration_event(
                event="build_created",
                build_id=str(build_id),
                data={"repo_url": request.repo_url, "objective": request.objective},
            )
            self._save_state_unlocked()
            return build

    async def get_build(self, build_id: UUID) -> BuildRun | None:
        async with self._lock:
            return self._builds.get(build_id)

    async def list_builds(
        self,
        *,
        user_id: str | None = None,
        status: BuildStatus | None = None,
        limit: int = 20,
    ) -> list[BuildRunSummary]:
        async with self._lock:
            rows = list(self._builds.values())
            if user_id:
                rows = [row for row in rows if row.created_by == user_id]
            if status is not None:
                rows = [row for row in rows if row.status == status]
            rows.sort(key=lambda row: row.created_at, reverse=True)
            rows = rows[: max(1, min(limit, 100))]
            return [
                BuildRunSummary(
                    build_id=row.build_id,
                    repo_url=row.repo_url,
                    objective=row.objective,
                    status=row.status,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    task_total=len(row.task_runs),
                    task_completed=sum(
                        1 for task in row.task_runs if task.status == TaskStatus.completed
                    ),
                    task_failed=sum(
                        1 for task in row.task_runs if task.status == TaskStatus.failed
                    ),
                )
                for row in rows
            ]

    async def resume_build(self, build_id: UUID, *, reason: str | None = None) -> BuildRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if build.status in (BuildStatus.completed, BuildStatus.aborted):
                raise ValueError(f"cannot_resume_{build.status.value}")
            self._transition_build_status_unlocked(
                build=build,
                to_status=BuildStatus.running,
                reason=reason or "manual_resume",
                source="manual",
            )
            self._append_event_unlocked(
                BuildEvent(
                    event_type="BUILD_RESUMED",
                    build_id=build_id,
                    payload={"reason": reason or "manual_resume"},
                )
            )
            self._append_checkpoint_unlocked(
                build_id=build_id,
                status=build.status,
                reason=reason or "manual_resume",
            )
            self._append_checkpoint_event_unlocked(
                build_id=build_id,
                reason=reason or "manual_resume",
                status=build.status,
            )
            emit_orchestration_event(
                event="build_resumed",
                build_id=str(build_id),
                data={"reason": reason or "manual_resume"},
            )
            self._save_state_unlocked()
            return build

    async def abort_build(self, build_id: UUID, *, reason: str | None = None) -> BuildRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if build.status == BuildStatus.completed:
                raise ValueError("cannot_abort_completed")
            self._transition_build_status_unlocked(
                build=build,
                to_status=BuildStatus.aborted,
                reason=reason or "manual_abort",
                source="manual",
            )
            self._append_event_unlocked(
                BuildEvent(
                    event_type="BUILD_ABORTED",
                    build_id=build_id,
                    payload={"reason": reason or "manual_abort"},
                )
            )
            self._append_event_unlocked(
                BuildEvent(
                    event_type="BUILD_FINISHED",
                    build_id=build_id,
                    payload={"final_status": BuildStatus.aborted.value},
                )
            )
            self._append_checkpoint_unlocked(
                build_id=build_id,
                status=build.status,
                reason=reason or "manual_abort",
            )
            self._append_checkpoint_event_unlocked(
                build_id=build_id,
                reason=reason or "manual_abort",
                status=build.status,
            )
            emit_orchestration_event(
                event="build_aborted",
                build_id=str(build_id),
                data={"reason": reason or "manual_abort"},
            )
            self._save_state_unlocked()
            return build

    async def complete_build(self, build_id: UUID, *, reason: str = "runtime_completed") -> BuildRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if build.status == BuildStatus.completed:
                return build
            if build.status == BuildStatus.aborted:
                raise ValueError("cannot_complete_aborted")

            self._transition_build_status_unlocked(
                build=build,
                to_status=BuildStatus.completed,
                reason=reason,
                source="runtime",
            )
            self._append_event_unlocked(
                BuildEvent(
                    event_type="BUILD_FINISHED",
                    build_id=build_id,
                    payload={"final_status": BuildStatus.completed.value},
                )
            )
            self._append_checkpoint_unlocked(
                build_id=build_id,
                status=build.status,
                reason=reason,
            )
            self._append_checkpoint_event_unlocked(
                build_id=build_id,
                reason=reason,
                status=build.status,
            )
            emit_orchestration_event(
                event="build_completed",
                build_id=str(build_id),
                data={"reason": reason},
            )
            self._save_state_unlocked()
            return build

    async def fail_build(self, build_id: UUID, *, reason: str = "runtime_failed") -> BuildRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if build.status == BuildStatus.failed:
                return build
            if BuildStatus.failed not in _VALID_STATUS_TRANSITIONS.get(build.status, set()):
                raise ValueError(f"cannot_fail_{build.status.value}")

            self._transition_build_status_unlocked(
                build=build,
                to_status=BuildStatus.failed,
                reason=reason,
                source="runtime",
            )
            self._append_event_unlocked(
                BuildEvent(
                    event_type="BUILD_FINISHED",
                    build_id=build_id,
                    payload={"final_status": BuildStatus.failed.value},
                )
            )
            self._append_checkpoint_unlocked(
                build_id=build_id,
                status=build.status,
                reason=reason,
            )
            self._append_checkpoint_event_unlocked(
                build_id=build_id,
                reason=reason,
                status=build.status,
            )
            emit_orchestration_event(
                event="build_failed",
                build_id=str(build_id),
                data={"reason": reason},
            )
            self._save_state_unlocked()
            return build

    async def start_task_run(
        self,
        build_id: UUID,
        *,
        node_id: str,
        source: str = "runtime_tick",
    ) -> TaskRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if not any(node.node_id == node_id for node in build.dag):
                raise KeyError("dag_node_not_found")
            if build.status != BuildStatus.running:
                raise ValueError(f"cannot_start_task_when_{build.status.value}")

            previous_attempt = max(
                (task.attempt for task in build.task_runs if task.node_id == node_id),
                default=0,
            )
            task_run = TaskRun(
                task_run_id=uuid4(),
                node_id=node_id,
                attempt=previous_attempt + 1,
                status=TaskStatus.running,
                started_at=utc_now(),
            )
            build.task_runs.append(task_run)
            self._set_node_status_unlocked(build=build, node_id=node_id, status=TaskStatus.running)
            build.updated_at = task_run.started_at
            self._append_event_unlocked(
                BuildEvent(
                    event_type="TASK_STARTED",
                    build_id=build_id,
                    payload={
                        "node_id": node_id,
                        "task_run_id": str(task_run.task_run_id),
                        "attempt": task_run.attempt,
                        "source": source,
                    },
                )
            )
            emit_orchestration_event(
                event="task_started",
                build_id=str(build_id),
                node_id=node_id,
                data={"task_run_id": str(task_run.task_run_id), "attempt": task_run.attempt},
            )
            self._save_state_unlocked()
            return task_run

    async def finish_task_run(
        self,
        build_id: UUID,
        *,
        task_run_id: UUID,
        status: TaskStatus,
        error: str | None = None,
        source: str = "runtime_tick",
    ) -> TaskRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")

            task_run = next(
                (task for task in build.task_runs if task.task_run_id == task_run_id),
                None,
            )
            if task_run is None:
                raise KeyError("task_run_not_found")
            if task_run.status in {TaskStatus.completed, TaskStatus.failed, TaskStatus.skipped}:
                raise ValueError("task_already_finalized")
            if status not in {TaskStatus.completed, TaskStatus.failed, TaskStatus.skipped}:
                raise ValueError("task_final_status_required")

            task_run.status = status
            task_run.finished_at = utc_now()
            task_run.error = error
            build.updated_at = task_run.finished_at
            self._set_node_status_unlocked(
                build=build,
                node_id=task_run.node_id,
                status=status,
            )
            event_type_by_status = {
                TaskStatus.completed: "TASK_COMPLETED",
                TaskStatus.failed: "TASK_FAILED",
                TaskStatus.skipped: "TASK_SKIPPED",
            }
            self._append_event_unlocked(
                BuildEvent(
                    event_type=event_type_by_status[status],
                    build_id=build_id,
                    payload={
                        "node_id": task_run.node_id,
                        "task_run_id": str(task_run.task_run_id),
                        "attempt": task_run.attempt,
                        "error": error,
                        "source": source,
                    },
                )
            )
            emit_orchestration_event(
                event="task_finished",
                build_id=str(build_id),
                node_id=task_run.node_id,
                data={
                    "task_run_id": str(task_run.task_run_id),
                    "status": status.value,
                    "attempt": task_run.attempt,
                },
            )
            self._save_state_unlocked()
            return task_run

    async def complete_task_run(
        self,
        build_id: UUID,
        *,
        task_run_id: UUID,
        status: TaskStatus,
        error: str | None = None,
        source: str = "manual",
    ) -> TaskRun:
        return await self.finish_task_run(
            build_id,
            task_run_id=task_run_id,
            status=status,
            error=error,
            source=source,
        )

    async def list_task_runs(
        self,
        build_id: UUID,
        *,
        node_id: str | None = None,
        status: TaskStatus | None = None,
        limit: int = 200,
    ) -> list[TaskRun]:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            rows = list(build.task_runs)
            if node_id is not None:
                rows = [row for row in rows if row.node_id == node_id]
            if status is not None:
                rows = [row for row in rows if row.status == status]
            rows.sort(key=lambda row: row.started_at, reverse=True)
            return rows[: max(1, min(limit, 500))]

    async def get_task_run(self, build_id: UUID, task_run_id: UUID) -> TaskRun | None:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            return next(
                (task for task in build.task_runs if task.task_run_id == task_run_id),
                None,
            )

    async def record_gate_decision(
        self,
        build_id: UUID,
        *,
        gate: GateType,
        status: GateDecisionStatus,
        reason: str,
        node_id: str | None = None,
        source: str = "runtime_tick",
    ) -> GateDecision:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")

            decision = GateDecision(
                decision_id=uuid4(),
                build_id=build_id,
                gate=gate,
                status=status,
                reason=reason,
                node_id=node_id,
            )
            build.gate_history.append(decision)
            build.updated_at = decision.created_at
            self._append_event_unlocked(
                BuildEvent(
                    event_type=gate.value,
                    build_id=build_id,
                    payload={
                        "decision_id": str(decision.decision_id),
                        "gate": gate.value,
                        "status": status.value,
                        "reason": reason,
                        "node_id": node_id,
                        "source": source,
                    },
                )
            )
            emit_orchestration_event(
                event="gate_decision",
                build_id=str(build_id),
                node_id=node_id,
                data={"gate": gate.value, "status": status.value, "reason": reason},
            )

            if status == GateDecisionStatus.blocked:
                if BuildStatus.paused in _VALID_STATUS_TRANSITIONS.get(build.status, set()):
                    self._transition_build_status_unlocked(
                        build=build,
                        to_status=BuildStatus.paused,
                        reason=f"{gate.value}:{reason}",
                        source="gate",
                    )
            if status == GateDecisionStatus.fail:
                if BuildStatus.failed in _VALID_STATUS_TRANSITIONS.get(build.status, set()):
                    self._transition_build_status_unlocked(
                        build=build,
                        to_status=BuildStatus.failed,
                        reason=f"{gate.value}:{reason}",
                        source="gate",
                    )
                    self._append_event_unlocked(
                        BuildEvent(
                            event_type="BUILD_FINISHED",
                            build_id=build_id,
                            payload={"final_status": BuildStatus.failed.value},
                        )
                    )
            self._save_state_unlocked()
            return decision

    async def list_gate_decisions(
        self,
        build_id: UUID,
        *,
        gate: GateType | None = None,
        limit: int = 200,
    ) -> list[GateDecision]:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            rows = list(build.gate_history)
            if gate is not None:
                rows = [row for row in rows if row.gate == gate]
            rows.sort(key=lambda row: row.created_at, reverse=True)
            return rows[: max(1, min(limit, 500))]

    async def record_replan_decision(
        self,
        build_id: UUID,
        *,
        action: ReplanAction,
        reason: str,
        replacement_nodes: list[DagNode] | None = None,
        source: str = "manual",
    ) -> ReplanDecision:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")

            replacement = list(replacement_nodes or [])
            if action == ReplanAction.modify_dag and replacement:
                existing_ids = {node.node_id for node in build.dag}
                duplicate_ids = [node.node_id for node in replacement if node.node_id in existing_ids]
                if duplicate_ids:
                    raise ValueError(f"duplicate_replan_node_id:{duplicate_ids[0]}")

            decision = ReplanDecision(
                decision_id=uuid4(),
                action=action,
                reason=reason,
                replacement_nodes=replacement,
            )
            build.replan_history.append(decision)
            build.updated_at = decision.created_at

            if action == ReplanAction.modify_dag and replacement:
                build.dag.extend(replacement)
                self._refresh_dag_levels_unlocked(build)

            if action == ReplanAction.abort and BuildStatus.aborted in _VALID_STATUS_TRANSITIONS.get(
                build.status,
                set(),
            ):
                self._transition_build_status_unlocked(
                    build=build,
                    to_status=BuildStatus.aborted,
                    reason=f"replan_abort:{reason}",
                    source="replanner",
                )
                self._append_event_unlocked(
                    BuildEvent(
                        event_type="BUILD_FINISHED",
                        build_id=build_id,
                        payload={"final_status": BuildStatus.aborted.value},
                    )
                )

            self._append_event_unlocked(
                BuildEvent(
                    event_type="REPLAN_DECISION",
                    build_id=build_id,
                    payload={
                        "decision_id": str(decision.decision_id),
                        "action": action.value,
                        "reason": reason,
                        "replacement_node_ids": [node.node_id for node in replacement],
                        "source": source,
                    },
                )
            )
            emit_orchestration_event(
                event="replan_decision",
                build_id=str(build_id),
                data={
                    "decision_id": str(decision.decision_id),
                    "action": action.value,
                    "reason": reason,
                    "source": source,
                },
            )
            self._save_state_unlocked()
            return decision

    async def list_replan_decisions(
        self,
        build_id: UUID,
        *,
        limit: int = 200,
    ) -> list[ReplanDecision]:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            rows = list(build.replan_history)
            rows.sort(key=lambda row: row.created_at, reverse=True)
            return rows[: max(1, min(limit, 500))]

    async def suggest_replan_decision(
        self,
        build_id: UUID,
        *,
        source: str = "debt_triage",
    ) -> ReplanSuggestion:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")

            blocking_violations = [row for row in build.policy_violations if row.blocking]
            if blocking_violations:
                codes = ",".join(sorted({row.code for row in blocking_violations}))
                suggestion = ReplanSuggestion(
                    action=ReplanAction.abort,
                    reason=f"blocking_policy_violation:{codes}",
                    replacement_nodes=[],
                )
            else:
                critical_debt = [
                    row for row in build.debt_items if self._severity_rank(row.severity) >= 4
                ]
                high_debt = [
                    row for row in build.debt_items if self._severity_rank(row.severity) >= 3
                ]
                medium_debt = [
                    row for row in build.debt_items if self._severity_rank(row.severity) >= 2
                ]

                if critical_debt:
                    suggestion = ReplanSuggestion(
                        action=ReplanAction.reduce_scope,
                        reason=f"critical_debt_detected:{len(critical_debt)}",
                        replacement_nodes=[],
                    )
                elif len(high_debt) >= 2:
                    suggestion = ReplanSuggestion(
                        action=ReplanAction.modify_dag,
                        reason=f"high_severity_debt:{len(high_debt)}",
                        replacement_nodes=self._build_debt_replacement_nodes_unlocked(
                            build=build,
                            debt_items=high_debt[:2],
                        ),
                    )
                elif len(medium_debt) >= 3:
                    suggestion = ReplanSuggestion(
                        action=ReplanAction.modify_dag,
                        reason=f"medium_severity_debt:{len(medium_debt)}",
                        replacement_nodes=self._build_debt_replacement_nodes_unlocked(
                            build=build,
                            debt_items=medium_debt[:1],
                        ),
                    )
                else:
                    suggestion = ReplanSuggestion(
                        action=ReplanAction.continue_,
                        reason="debt_below_triage_threshold",
                        replacement_nodes=[],
                    )

            self._append_event_unlocked(
                BuildEvent(
                    event_type="REPLAN_SUGGESTED",
                    build_id=build_id,
                    payload={
                        "action": suggestion.action.value,
                        "reason": suggestion.reason,
                        "replacement_node_ids": [
                            node.node_id for node in suggestion.replacement_nodes
                        ],
                        "source": source,
                    },
                )
            )
            self._save_state_unlocked()
            return suggestion

    async def apply_suggested_replan(
        self,
        build_id: UUID,
        *,
        reason_override: str | None = None,
        source: str = "debt_triage",
    ) -> ReplanDecision:
        suggestion = await self.suggest_replan_decision(build_id, source=source)
        return await self.record_replan_decision(
            build_id,
            action=suggestion.action,
            reason=reason_override or suggestion.reason,
            replacement_nodes=suggestion.replacement_nodes,
            source=source,
        )

    async def record_debt_item(
        self,
        build_id: UUID,
        *,
        node_id: str,
        summary: str,
        severity: str = "medium",
        source: str = "manual",
    ) -> DebtItem:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            item = DebtItem(
                debt_id=uuid4(),
                node_id=node_id,
                summary=summary,
                severity=severity,
            )
            build.debt_items.append(item)
            build.updated_at = item.created_at
            self._append_event_unlocked(
                BuildEvent(
                    event_type="DEBT_ITEM_RECORDED",
                    build_id=build_id,
                    payload={
                        "debt_id": str(item.debt_id),
                        "node_id": node_id,
                        "severity": severity,
                        "summary": summary,
                        "source": source,
                    },
                )
            )
            self._save_state_unlocked()
            return item

    async def list_debt_items(
        self,
        build_id: UUID,
        *,
        limit: int = 200,
    ) -> list[DebtItem]:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            rows = list(build.debt_items)
            rows.sort(key=lambda row: row.created_at, reverse=True)
            return rows[: max(1, min(limit, 500))]

    async def record_policy_violation(
        self,
        build_id: UUID,
        *,
        code: str,
        message: str,
        source: str,
        blocking: bool = True,
    ) -> PolicyViolation:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            violation = PolicyViolation(
                violation_id=uuid4(),
                code=code,
                message=message,
                source=source,
                blocking=blocking,
            )
            build.policy_violations.append(violation)
            build.updated_at = violation.created_at
            self._append_event_unlocked(
                BuildEvent(
                    event_type="POLICY_VIOLATION",
                    build_id=build_id,
                    payload={
                        "violation_id": str(violation.violation_id),
                        "code": code,
                        "message": message,
                        "source": source,
                        "blocking": blocking,
                    },
                )
            )
            if blocking and BuildStatus.failed in _VALID_STATUS_TRANSITIONS.get(build.status, set()):
                self._transition_build_status_unlocked(
                    build=build,
                    to_status=BuildStatus.failed,
                    reason=f"policy_violation:{code}",
                    source="policy",
                )
                self._append_event_unlocked(
                    BuildEvent(
                        event_type="BUILD_FINISHED",
                        build_id=build_id,
                        payload={"final_status": BuildStatus.failed.value},
                    )
                )
            self._save_state_unlocked()
            return violation

    async def list_policy_violations(
        self,
        build_id: UUID,
        *,
        limit: int = 200,
    ) -> list[PolicyViolation]:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            rows = list(build.policy_violations)
            rows.sort(key=lambda row: row.created_at, reverse=True)
            return rows[: max(1, min(limit, 500))]

    async def create_checkpoint(
        self,
        build_id: UUID,
        *,
        reason: str,
    ) -> BuildCheckpoint:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            checkpoint = self._append_checkpoint_unlocked(
                build_id=build_id,
                status=build.status,
                reason=reason,
            )
            self._append_checkpoint_event_unlocked(
                build_id=build_id,
                reason=reason,
                status=build.status,
            )
            self._save_state_unlocked()
            return checkpoint

    async def list_checkpoints(self, build_id: UUID) -> list[BuildCheckpoint]:
        async with self._lock:
            return list(self._checkpoints.get(build_id, []))

    async def list_events(self, build_id: UUID) -> list[BuildEvent]:
        async with self._lock:
            return list(self._events.get(build_id, []))

    async def append_event(
        self,
        build_id: UUID,
        *,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        async with self._lock:
            if build_id not in self._builds:
                raise KeyError("build_not_found")
            self._append_event_unlocked(
                BuildEvent(
                    event_type=event_type,
                    build_id=build_id,
                    payload=payload or {},
                )
            )
            self._save_state_unlocked()

    def _append_event_unlocked(self, event: BuildEvent) -> None:
        self._events[event.build_id].append(event)

    def _refresh_dag_levels_unlocked(self, build: BuildRun) -> None:
        levels = compute_dag_levels(build.dag)
        build.metadata["dag_levels"] = levels
        cursor = int(build.metadata.get("level_cursor", 0))
        if levels:
            build.metadata["level_cursor"] = max(0, min(cursor, len(levels) - 1))
        else:
            build.metadata["level_cursor"] = 0

    def _append_checkpoint_unlocked(
        self,
        *,
        build_id: UUID,
        status: BuildStatus,
        reason: str,
    ) -> BuildCheckpoint:
        checkpoint = BuildCheckpoint(
            checkpoint_id=uuid4(),
            build_id=build_id,
            status=status,
            reason=reason,
            event_cursor=len(self._events.get(build_id, [])),
        )
        self._checkpoints[build_id].append(checkpoint)
        return checkpoint

    def _append_checkpoint_event_unlocked(
        self,
        *,
        build_id: UUID,
        reason: str,
        status: BuildStatus,
    ) -> None:
        latest = self._checkpoints.get(build_id, [])
        checkpoint_id = latest[-1].checkpoint_id if latest else None
        self._append_event_unlocked(
            BuildEvent(
                event_type="CHECKPOINT_CREATED",
                build_id=build_id,
                payload={
                    "checkpoint_id": str(checkpoint_id) if checkpoint_id else None,
                    "reason": reason,
                    "status": status.value,
                },
            )
        )

    def _set_node_status_unlocked(
        self,
        *,
        build: BuildRun,
        node_id: str,
        status: TaskStatus,
    ) -> None:
        for node in build.dag:
            if node.node_id == node_id:
                node.status = status
                return

    def _severity_rank(self, severity: str) -> int:
        normalized = severity.strip().lower()
        mapping = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        return mapping.get(normalized, 2)

    def _build_debt_replacement_nodes_unlocked(
        self,
        *,
        build: BuildRun,
        debt_items: list[DebtItem],
    ) -> list[DagNode]:
        existing_ids = {node.node_id for node in build.dag}
        created: list[DagNode] = []
        for debt_item in debt_items:
            base_id = f"debt-remediation-{debt_item.node_id}"
            node_id = self._next_unique_node_id_unlocked(
                base_id=base_id,
                existing_ids=existing_ids,
            )
            existing_ids.add(node_id)
            depends_on = [debt_item.node_id] if debt_item.node_id in existing_ids else []
            created.append(
                DagNode(
                    node_id=node_id,
                    title=f"Debt remediation: {debt_item.node_id}",
                    agent="planner",
                    depends_on=depends_on,
                )
            )
        return created

    def _next_unique_node_id_unlocked(
        self,
        *,
        base_id: str,
        existing_ids: set[str],
    ) -> str:
        if base_id not in existing_ids:
            return base_id
        cursor = 2
        while f"{base_id}-{cursor}" in existing_ids:
            cursor += 1
        return f"{base_id}-{cursor}"

    def _transition_build_status_unlocked(
        self,
        *,
        build: BuildRun,
        to_status: BuildStatus,
        reason: str,
        source: str,
    ) -> BuildStatusTransition | None:
        from_status = build.status
        if from_status == to_status:
            return None
        if to_status not in _VALID_STATUS_TRANSITIONS.get(from_status, set()):
            raise ValueError(
                f"invalid_transition_{from_status.value}_to_{to_status.value}"
            )

        transition = BuildStatusTransition(
            transition_id=uuid4(),
            from_status=from_status,
            to_status=to_status,
            reason=reason,
            source=source,
        )
        build.status = to_status
        build.updated_at = transition.created_at
        build.state_transitions.append(transition)
        self._append_event_unlocked(
            BuildEvent(
                event_type="BUILD_STATUS_CHANGED",
                build_id=build.build_id,
                payload={
                    "transition_id": str(transition.transition_id),
                    "from_status": from_status.value,
                    "to_status": to_status.value,
                    "reason": reason,
                    "source": source,
                },
            )
        )
        emit_orchestration_event(
            event="build_status_changed",
            build_id=str(build.build_id),
            data={
                "from_status": from_status.value,
                "to_status": to_status.value,
                "reason": reason,
                "source": source,
            },
        )
        return transition

    def _load_state(self) -> None:
        payload: dict[str, Any] | None = None
        try:
            asyncio.get_running_loop()
            loop_running = True
        except RuntimeError:
            loop_running = False

        if not loop_running:
            try:
                payload = asyncio.run(load_state_snapshot(self._state_key))
            except Exception:
                logger.warning("Failed to load build store snapshot from Supabase.")
                payload = None

        if payload is None and self._state_path and self._state_path.exists():
            try:
                payload = json.loads(self._state_path.read_text())
            except Exception:
                logger.warning("Failed to load build store snapshot from local state file.")
                payload = None

        if not isinstance(payload, dict):
            return

        builds_raw = payload.get("builds") or {}
        events_raw = payload.get("events") or {}
        checkpoints_raw = payload.get("checkpoints") or {}

        loaded_builds: dict[UUID, BuildRun] = {}
        loaded_events: dict[UUID, list[BuildEvent]] = {}
        loaded_checkpoints: dict[UUID, list[BuildCheckpoint]] = {}

        for build_key, build_payload in builds_raw.items():
            try:
                build = BuildRun.model_validate(build_payload)
                build_id = UUID(str(build_key))
                loaded_builds[build_id] = build
            except Exception:
                continue

        for build_key, rows in events_raw.items():
            try:
                build_id = UUID(str(build_key))
            except Exception:
                continue
            parsed: list[BuildEvent] = []
            if isinstance(rows, list):
                for row in rows:
                    try:
                        parsed.append(BuildEvent.model_validate(row))
                    except Exception:
                        continue
            loaded_events[build_id] = parsed

        for build_key, rows in checkpoints_raw.items():
            try:
                build_id = UUID(str(build_key))
            except Exception:
                continue
            parsed: list[BuildCheckpoint] = []
            if isinstance(rows, list):
                for row in rows:
                    try:
                        parsed.append(BuildCheckpoint.model_validate(row))
                    except Exception:
                        continue
            loaded_checkpoints[build_id] = parsed

        self._builds = loaded_builds
        self._events = defaultdict(list, loaded_events)
        self._checkpoints = defaultdict(list, loaded_checkpoints)

    def _save_state_unlocked(self) -> None:
        payload = self._serialize_state_unlocked()

        if self._state_path:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._state_path.with_suffix(f"{self._state_path.suffix}.tmp")
            tmp_path.write_text(json.dumps(payload))
            tmp_path.replace(self._state_path)

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(save_state_snapshot(self._state_key, payload))
        except RuntimeError:
            try:
                asyncio.run(save_state_snapshot(self._state_key, payload))
            except Exception:
                logger.warning("Failed to save build store snapshot to Supabase.")
        except Exception:
            logger.warning("Failed to enqueue build store snapshot save.")

    def _serialize_state_unlocked(self) -> dict[str, Any]:
        return {
            "builds": {
                str(build_id): build.model_dump(mode="json")
                for build_id, build in self._builds.items()
            },
            "events": {
                str(build_id): [event.model_dump(mode="json") for event in rows]
                for build_id, rows in self._events.items()
            },
            "checkpoints": {
                str(build_id): [row.model_dump(mode="json") for row in rows]
                for build_id, rows in self._checkpoints.items()
            },
        }


build_store = BuildStore()
