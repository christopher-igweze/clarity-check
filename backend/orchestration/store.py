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
    DagNode,
    TaskRun,
    TaskStatus,
    utc_now,
)


def _default_dag() -> list[DagNode]:
    return [
        DagNode(node_id="scanner", title="Static scan", agent="scanner", depends_on=[]),
        DagNode(node_id="builder", title="Dynamic probe", agent="builder", depends_on=["scanner"]),
        DagNode(node_id="security", title="Security review", agent="security", depends_on=["builder"]),
        DagNode(node_id="planner", title="Remediation plan", agent="planner", depends_on=["security"]),
    ]


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
                status=BuildStatus.running,
                created_at=now,
                updated_at=now,
                dag=request.dag or _default_dag(),
                metadata=request.metadata,
            )
            self._builds[build_id] = build
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

            build.status = BuildStatus.running
            build.updated_at = utc_now()
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
            return build

    async def abort_build(self, build_id: UUID, *, reason: str | None = None) -> BuildRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if build.status == BuildStatus.completed:
                raise ValueError("cannot_abort_completed")

            build.status = BuildStatus.aborted
            build.updated_at = utc_now()
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
            return build

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

    async def start_task_run(self, build_id: UUID, *, node_id: str) -> TaskRun:
        async with self._lock:
            build = self._builds.get(build_id)
            if build is None:
                raise KeyError("build_not_found")
            if not any(node.node_id == node_id for node in build.dag):
                raise KeyError("dag_node_not_found")

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
                        "task_run_id": str(task_run.task_run_id),
                        "node_id": node_id,
                        "attempt": task_run.attempt,
                    },
                )
            )
            return task_run

    async def complete_task_run(
        self,
        build_id: UUID,
        *,
        task_run_id: UUID,
        status: TaskStatus,
        error: str | None = None,
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
                raise ValueError("task_run_already_finalized")
            if status not in {TaskStatus.completed, TaskStatus.failed, TaskStatus.skipped}:
                raise ValueError("task_run_invalid_final_status")

            task_run.status = status
            task_run.finished_at = utc_now()
            task_run.error = error
            build.updated_at = task_run.finished_at
            self._set_node_status_unlocked(
                build=build,
                node_id=task_run.node_id,
                status=status,
            )

            event_type_map = {
                TaskStatus.completed: "TASK_COMPLETED",
                TaskStatus.failed: "TASK_FAILED",
                TaskStatus.skipped: "TASK_SKIPPED",
            }
            self._append_event_unlocked(
                BuildEvent(
                    event_type=event_type_map[status],
                    build_id=build_id,
                    payload={
                        "task_run_id": str(task_run.task_run_id),
                        "node_id": task_run.node_id,
                        "attempt": task_run.attempt,
                        "error": error,
                    },
                )
            )
            return task_run

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
                (row for row in build.task_runs if row.task_run_id == task_run_id),
                None,
            )

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


build_store = BuildStore()
