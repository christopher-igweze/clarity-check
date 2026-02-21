"""Tests for backend-owned runtime orchestration worker."""

from __future__ import annotations

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")
os.environ.setdefault("CONTROL_PLANE_USE_SUPABASE", "false")

from models.builds import BuildCreateRequest  # noqa: E402
from orchestration.runtime_worker import RuntimeWorker  # noqa: E402
from orchestration.store import build_store  # noqa: E402
from services.ephemeral_coordination import CoordinationUnavailableError  # noqa: E402


class RuntimeWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_worker_completes_running_build_without_manual_ticks(self) -> None:
        build = await build_store.create_build(
            user_id="worker_test_user",
            request=BuildCreateRequest(
                repo_url="https://github.com/octocat/Hello-World",
                objective="worker-owned-runtime-test",
            ),
        )
        worker = RuntimeWorker(poll_seconds=0.05)
        worker.start()
        try:
            for _ in range(80):
                row = await build_store.get_build(build.build_id)
                if row is not None and row.status.value in {"completed", "failed", "aborted"}:
                    break
                await asyncio.sleep(0.05)
            final = await build_store.get_build(build.build_id)
            self.assertIsNotNone(final)
            self.assertEqual(final.status.value, "completed")
        finally:
            await worker.stop()

    async def test_worker_schedules_all_running_build_ids_without_hard_cap(self) -> None:
        build_ids = [uuid4() for _ in range(650)]
        worker = RuntimeWorker(poll_seconds=0.05)
        processed: list = []

        async def _process(build_id):
            processed.append(build_id)

        with (
            patch("orchestration.runtime_worker.build_store.list_running_build_ids", new=AsyncMock(return_value=build_ids)),
            patch("orchestration.runtime_worker.ephemeral_coordinator.acquire_lease", new=AsyncMock(return_value=True)),
            patch.object(worker, "_process_build", new=_process),
        ):
            await worker._tick_once()
            await asyncio.sleep(0)
            await asyncio.sleep(0)

        self.assertEqual(len(processed), len(build_ids))

    async def test_worker_stops_tick_when_coordination_is_unavailable(self) -> None:
        worker = RuntimeWorker(poll_seconds=0.05)
        with (
            patch("orchestration.runtime_worker.build_store.list_running_build_ids", new=AsyncMock(return_value=[uuid4()])),
            patch(
                "orchestration.runtime_worker.ephemeral_coordinator.acquire_lease",
                new=AsyncMock(side_effect=CoordinationUnavailableError("redis_unavailable")),
            ),
        ):
            with self.assertRaises(CoordinationUnavailableError):
                await worker._tick_once()


if __name__ == "__main__":
    unittest.main()
