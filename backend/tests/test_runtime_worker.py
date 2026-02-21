"""Tests for backend-owned runtime orchestration worker."""

from __future__ import annotations

import asyncio
import os
import unittest

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")
os.environ.setdefault("CONTROL_PLANE_USE_SUPABASE", "false")

from models.builds import BuildCreateRequest  # noqa: E402
from orchestration.runtime_worker import RuntimeWorker  # noqa: E402
from orchestration.store import build_store  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
