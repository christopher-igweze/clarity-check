"""Background runtime worker that owns orchestration ticks server-side."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID, uuid4

from config import settings
from models.builds import BuildStatus
from orchestration.runtime_gateway import runtime_gateway
from orchestration.runtime_tick import execute_runtime_tick
from orchestration.store import build_store
from services.ephemeral_coordination import (
    CoordinationUnavailableError,
    ephemeral_coordinator,
)

logger = logging.getLogger(__name__)


class RuntimeWorker:
    def __init__(
        self,
        *,
        poll_seconds: float = 0.75,
        lease_ttl_seconds: int | None = None,
    ) -> None:
        self._poll_seconds = max(0.2, float(poll_seconds))
        self._lease_ttl_seconds = max(
            5,
            int(lease_ttl_seconds or settings.runtime_worker_lease_ttl_seconds),
        )
        self._worker_id = f"runtime-worker-{uuid4()}"
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
            except CoordinationUnavailableError:
                logger.error(
                    "Runtime worker paused: distributed coordination is unavailable and fail-closed is enabled."
                )
            except Exception:
                logger.exception("Runtime worker tick loop error.")
            await asyncio.sleep(self._poll_seconds)

    async def _tick_once(self) -> None:
        running_build_ids = await build_store.list_running_build_ids()
        for build_id in running_build_ids:
            async with self._lock:
                if build_id in self._inflight:
                    continue
            lease_key = self._lease_key(build_id)
            claimed = await ephemeral_coordinator.acquire_lease(
                lease_key,
                owner=self._worker_id,
                ttl_seconds=self._lease_ttl_seconds,
            )
            if not claimed:
                continue
            async with self._lock:
                self._inflight.add(build_id)
            asyncio.create_task(self._process_build(build_id))

    async def _process_build(self, build_id: UUID) -> None:
        lease_key = self._lease_key(build_id)
        heartbeat_stop = asyncio.Event()
        heartbeat_task: asyncio.Task | None = None
        try:
            renewed = await ephemeral_coordinator.renew_lease(
                lease_key,
                owner=self._worker_id,
                ttl_seconds=self._lease_ttl_seconds,
            )
            if not renewed:
                return
            heartbeat_task = asyncio.create_task(
                self._lease_heartbeat(
                    lease_key,
                    stop_event=heartbeat_stop,
                )
            )
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
            heartbeat_stop.set()
            if heartbeat_task is not None:
                try:
                    await heartbeat_task
                except CoordinationUnavailableError:
                    logger.error(
                        "Runtime worker heartbeat failed while closing build=%s.",
                        build_id,
                    )
            try:
                await ephemeral_coordinator.release_lease(
                    lease_key,
                    owner=self._worker_id,
                )
            except CoordinationUnavailableError:
                logger.error(
                    "Runtime worker could not release lease for build=%s due to coordination outage.",
                    build_id,
                )
            async with self._lock:
                self._inflight.discard(build_id)

    def _lease_key(self, build_id: UUID) -> str:
        return f"runtime-build:{build_id}"

    async def _lease_heartbeat(self, lease_key: str, *, stop_event: asyncio.Event) -> None:
        interval = max(1.0, self._lease_ttl_seconds / 3)
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
                break
            except asyncio.TimeoutError:
                pass
            renewed = await ephemeral_coordinator.renew_lease(
                lease_key,
                owner=self._worker_id,
                ttl_seconds=self._lease_ttl_seconds,
            )
            if not renewed:
                raise CoordinationUnavailableError("runtime_worker_lease_lost")
