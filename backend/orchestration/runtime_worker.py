"""Background runtime worker that owns orchestration ticks server-side."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from models.builds import BuildStatus
from orchestration.runtime_gateway import runtime_gateway
from orchestration.runtime_tick import execute_runtime_tick
from orchestration.store import build_store

logger = logging.getLogger(__name__)


class RuntimeWorker:
    def __init__(self, *, poll_seconds: float = 0.75) -> None:
        self._poll_seconds = max(0.2, float(poll_seconds))
        self._task: asyncio.Task | None = None
        self._shutdown = asyncio.Event()
        self._inflight: set[UUID] = set()
        self._lock = asyncio.Lock()

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._shutdown.clear()
        self._task = asyncio.create_task(self._run_loop(), name="runtime-worker-loop")

    async def stop(self) -> None:
        self._shutdown.set()
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def _run_loop(self) -> None:
        while not self._shutdown.is_set():
            try:
                await self._tick_once()
            except Exception:
                logger.exception("Runtime worker tick loop error.")
            await asyncio.sleep(self._poll_seconds)

    async def _tick_once(self) -> None:
        running = await build_store.list_builds(status=BuildStatus.running, limit=500)
        for row in running:
            build_id = row.build_id
            async with self._lock:
                if build_id in self._inflight:
                    continue
                self._inflight.add(build_id)
            asyncio.create_task(self._process_build(build_id))

    async def _process_build(self, build_id: UUID) -> None:
        try:
            build = await build_store.get_build(build_id)
            if build is None or build.status != BuildStatus.running:
                return
            session = await runtime_gateway.get_session(build_id)
            if session is None:
                await runtime_gateway.bootstrap(build)
                await build_store.append_event(
                    build_id,
                    event_type="RUNTIME_BOOTSTRAPPED",
                    payload={"runtime_owner": "backend_worker"},
                )
            await execute_runtime_tick(build_id)
        except (KeyError, ValueError):
            # Build may have moved state between scheduling and execution.
            return
        except Exception:
            logger.exception("Runtime worker failed for build=%s", build_id)
        finally:
            async with self._lock:
                self._inflight.discard(build_id)
