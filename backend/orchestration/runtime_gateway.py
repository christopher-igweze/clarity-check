"""Week 1 runtime gateway bridging build DAGs to execution sessions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import UUID, uuid4

from models.builds import BuildRun, TaskStatus
from models.runtime import RuntimeSession, RuntimeTickResult
from orchestration.scheduler import compute_dag_levels, find_level
from orchestration.telemetry import emit_runtime_metric


@dataclass
class RuntimeState:
    session: RuntimeSession
    executed_nodes: set[str]
    level_cursor: int = 0


class RuntimeGateway:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._states: dict[UUID, RuntimeState] = {}

    async def bootstrap(self, build: BuildRun) -> RuntimeSession:
        async with self._lock:
            state = self._states.get(build.build_id)
            if state is not None:
                state.session.updated_at = state.session.updated_at  # keep stable type updates
                return state.session

            dag_levels = build.metadata.get("dag_levels")
            if not isinstance(dag_levels, list):
                dag_levels = compute_dag_levels(build.dag)
                build.metadata["dag_levels"] = dag_levels
            level_cursor = int(build.metadata.get("level_cursor", 0))

            session = RuntimeSession(
                runtime_id=uuid4(),
                build_id=build.build_id,
                status="bootstrapped",
                metadata={
                    "repo_url": build.repo_url,
                    "objective": build.objective,
                    "dag_nodes": [node.node_id for node in build.dag],
                    "level_count": len(dag_levels),
                },
            )
            self._states[build.build_id] = RuntimeState(
                session=session,
                executed_nodes=self._durable_executed_nodes(build),
                level_cursor=max(0, level_cursor),
            )
            emit_runtime_metric(
                metric="runtime_bootstrap",
                tags={"build_id": str(build.build_id)},
                fields={
                    "runtime_id": str(session.runtime_id),
                    "status": session.status,
                    "level_count": len(dag_levels),
                },
            )
            return session

    async def get_session(self, build_id: UUID) -> RuntimeSession | None:
        async with self._lock:
            state = self._states.get(build_id)
            if state is None:
                return None
            return state.session

    async def mark_node_for_retry(self, build: BuildRun, *, node_id: str) -> int | None:
        async with self._lock:
            state = self._states.get(build.build_id)
            if state is None:
                return None

            if node_id in state.executed_nodes:
                state.executed_nodes.remove(node_id)

            dag_levels = build.metadata.get("dag_levels")
            if not isinstance(dag_levels, list):
                dag_levels = compute_dag_levels(build.dag)
                build.metadata["dag_levels"] = dag_levels

            retry_level = find_level(dag_levels, node_id=node_id)
            if retry_level is not None:
                state.level_cursor = min(state.level_cursor, retry_level)
                build.metadata["level_cursor"] = state.level_cursor
            return retry_level

    async def reset_build_state(self, build: BuildRun, *, reason: str) -> RuntimeSession | None:
        async with self._lock:
            state = self._states.get(build.build_id)
            if state is None:
                return None
            state.executed_nodes = set()
            state.level_cursor = 0
            build.metadata["level_cursor"] = 0
            state.session.status = "running"
            state.session.metadata = {
                **state.session.metadata,
                "reset_reason": reason,
                "dag_nodes": [node.node_id for node in build.dag],
                "level_count": len(build.metadata.get("dag_levels", [])),
            }
            return state.session

    async def tick(self, build: BuildRun) -> RuntimeTickResult:
        async with self._lock:
            dag_levels = build.metadata.get("dag_levels")
            if not isinstance(dag_levels, list):
                dag_levels = compute_dag_levels(build.dag)
                build.metadata["dag_levels"] = dag_levels

            durable_executed = self._durable_executed_nodes(build)
            state = self._states.get(build.build_id)
            if state is None:
                session = RuntimeSession(
                    runtime_id=uuid4(),
                    build_id=build.build_id,
                    status="running",
                    metadata={"auto_bootstrap": True},
                )
                level_cursor = int(build.metadata.get("level_cursor", 0))
                state = RuntimeState(
                    session=session,
                    executed_nodes=set(durable_executed),
                    level_cursor=max(0, level_cursor),
                )
                self._states[build.build_id] = state
            else:
                # Rehydrate execution progress from durable task state on every tick.
                state.executed_nodes = set(durable_executed)

            state.session.status = "running"

            active_level = state.level_cursor if state.level_cursor < len(dag_levels) else None
            level_node_ids = (
                set(dag_levels[state.level_cursor])
                if active_level is not None
                else set()
            )
            ready_nodes = [
                node
                for node in build.dag
                if node.node_id in level_node_ids
                and node.node_id not in state.executed_nodes
                and all(dep in state.executed_nodes for dep in node.depends_on)
            ]
            executed: list[str] = []
            for node in ready_nodes:
                state.executed_nodes.add(node.node_id)
                executed.append(node.node_id)

            level_completed = None
            level_started = None
            if active_level is not None:
                level_complete = all(
                    node_id in state.executed_nodes for node_id in dag_levels[active_level]
                )
                if level_complete:
                    level_completed = active_level
                    if active_level + 1 < len(dag_levels):
                        state.level_cursor = active_level + 1
                        level_started = state.level_cursor
                        build.metadata["level_cursor"] = state.level_cursor

            pending_nodes = [
                node.node_id
                for node in build.dag
                if node.node_id not in state.executed_nodes
            ]
            finished = len(pending_nodes) == 0
            state.session.status = "completed" if finished else "running"

            emit_runtime_metric(
                metric="runtime_tick",
                value=len(executed),
                tags={
                    "build_id": str(build.build_id),
                    "runtime_id": str(state.session.runtime_id),
                },
                fields={
                    "pending": len(pending_nodes),
                    "finished": finished,
                    "status": state.session.status,
                    "active_level": active_level,
                    "level_started": level_started,
                    "level_completed": level_completed,
                },
            )

            return RuntimeTickResult(
                build_id=build.build_id,
                runtime_id=state.session.runtime_id,
                executed_nodes=executed,
                pending_nodes=pending_nodes,
                active_level=active_level,
                level_started=level_started,
                level_completed=level_completed,
                finished=finished,
            )

    @staticmethod
    def _durable_executed_nodes(build: BuildRun) -> set[str]:
        return {
            task.node_id
            for task in build.task_runs
            if task.status in {TaskStatus.completed, TaskStatus.skipped}
        }


runtime_gateway = RuntimeGateway()
