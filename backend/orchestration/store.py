"""In-memory orchestration state store for Week 1 control-plane scaffolding."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any
from uuid import UUID, uuid4

from models.builds import (
    BuildCheckpoint,
    BuildCreateRequest,
    BuildEvent,
    BuildRun,
    BuildRunSummary,
    BuildStatus,
    BuildStatusTransition,
    DagNode,
    GateDecision,
    GateDecisionStatus,
    GateType,
    TaskRun,
    TaskStatus,
    utc_now,
)
from orchestration.telemetry import emit_orchestration_event


def _default_dag() -> list[DagNode]:
    return [
        DagNode(node_id="scanner", title="Static scan", agent="scanner", depends_on=[]),
        DagNode(node_id="builder", title="Dynamic probe", agent="builder", depends_on=["scanner"]),
        DagNode(node_id="security", title="Security review", agent="security", depends_on=["builder"]),
        DagNode(node_id="planner", title="Remediation plan", agent="planner", depends_on=["security"]),
    ]


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
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._builds: dict[UUID, BuildRun] = {}
        self._events: dict[UUID, list[BuildEvent]] = defaultdict(list)
        self._checkpoints: dict[UUID, list[BuildCheckpoint]] = defaultdict(list)

    async def create_build(self, *, user_id: str, request: BuildCreateRequest) -> BuildRun:
        async with self._lock:
            build_id = uuid4()
            now = utc_now()
            build = BuildRun(
                build_id=build_id,
                created_by=user_id,
                repo_url=request.repo_url,
                objective=request.objective,
                status=BuildStatus.pending,
                created_at=now,
                updated_at=now,
                dag=request.dag or _default_dag(),
                metadata=request.metadata,
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
                        "dag_nodes": [node.node_id for node in build.dag],
                    },
                )
            )
            if build.dag:
                level_zero_nodes = [
                    node.node_id for node in build.dag if not node.depends_on
                ]
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

    def _append_event_unlocked(self, event: BuildEvent) -> None:
        self._events[event.build_id].append(event)

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


build_store = BuildStore()
