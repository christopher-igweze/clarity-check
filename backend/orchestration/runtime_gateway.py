"""Week 1 runtime gateway bridging build DAGs to execution sessions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import UUID, uuid4

from models.builds import BuildRun
from models.runtime import RuntimeSession, RuntimeTickResult
from orchestration.telemetry import emit_runtime_metric


@dataclass
class RuntimeState:
    session: RuntimeSession
    executed_nodes: set[str]


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

            session = RuntimeSession(
                runtime_id=uuid4(),
                build_id=build.build_id,
                status="bootstrapped",
                metadata={
                    "repo_url": build.repo_url,
                    "objective": build.objective,
                    "dag_nodes": [node.node_id for node in build.dag],
                },
            )
            self._states[build.build_id] = RuntimeState(
                session=session,
                executed_nodes=set(),
            )
            emit_runtime_metric(
                metric="runtime_bootstrap",
                tags={"build_id": str(build.build_id)},
                fields={"runtime_id": str(session.runtime_id)},
            )
            return session

    async def get_session(self, build_id: UUID) -> RuntimeSession | None:
        async with self._lock:
            state = self._states.get(build_id)
            if state is None:
                return None
            return state.session

    async def tick(self, build: BuildRun) -> RuntimeTickResult:
        async with self._lock:
            state = self._states.get(build.build_id)
            if state is None:
                session = RuntimeSession(
                    runtime_id=uuid4(),
                    build_id=build.build_id,
                    status="running",
                    metadata={"auto_bootstrap": True},
                )
                state = RuntimeState(session=session, executed_nodes=set())
                self._states[build.build_id] = state

            state.session.status = "running"

            ready_nodes = [
                node
                for node in build.dag
                if node.node_id not in state.executed_nodes
                and all(dep in state.executed_nodes for dep in node.depends_on)
            ]
            executed: list[str] = []
            for node in ready_nodes:
                state.executed_nodes.add(node.node_id)
                executed.append(node.node_id)

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
                fields={"pending": len(pending_nodes), "finished": finished},
            )

            return RuntimeTickResult(
                build_id=build.build_id,
                runtime_id=state.session.runtime_id,
                executed_nodes=executed,
                pending_nodes=pending_nodes,
                finished=finished,
            )


runtime_gateway = RuntimeGateway()

