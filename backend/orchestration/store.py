"""In-memory orchestration state store for Week 1 control-plane scaffolding."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any
from uuid import UUID, uuid4

from models.builds import (
    BuildCreateRequest,
    BuildEvent,
    BuildRun,
    BuildStatus,
    DagNode,
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
            return build

    async def get_build(self, build_id: UUID) -> BuildRun | None:
        async with self._lock:
            return self._builds.get(build_id)

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
            return build

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


build_store = BuildStore()

