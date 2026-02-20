"""Unit tests for runner bridge normalization and log recording."""

from __future__ import annotations

import asyncio
import os
import unittest
from uuid import uuid4

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from models.builds import BuildRun, BuildStatus, DagNode, utc_now  # noqa: E402
from orchestration.runner_bridge import normalize_runner_status, runner_bridge  # noqa: E402


def _build_with_overrides(status: str) -> BuildRun:
    build_id = uuid4()
    now = utc_now()
    return BuildRun(
        build_id=build_id,
        created_by="user_test",
        repo_url="https://github.com/octocat/Hello-World",
        objective="runner bridge test",
        status=BuildStatus.running,
        created_at=now,
        updated_at=now,
        dag=[DagNode(node_id="scanner", title="scan", agent="scanner", depends_on=[])],
        metadata={
            "runner_results": {
                "scanner": {
                    "runner": "openhands",
                    "workspace_id": "workspace-1",
                    "status": status,
                    "duration_ms": 320,
                }
            }
        },
    )


class RunnerBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        asyncio.run(runner_bridge.reset())

    def test_status_normalization_maps_common_values(self) -> None:
        self.assertEqual(normalize_runner_status("ok"), "completed")
        self.assertEqual(normalize_runner_status("SUCCESS"), "completed")
        self.assertEqual(normalize_runner_status("failed"), "failed")
        self.assertEqual(normalize_runner_status("skip"), "skipped")
        self.assertEqual(normalize_runner_status("unexpected-value"), "completed")

    def test_execute_records_failed_log_with_workspace(self) -> None:
        build = _build_with_overrides("failed")
        runtime_id = uuid4()

        record = asyncio.run(
            runner_bridge.execute(
                build=build,
                runtime_id=runtime_id,
                node_id="scanner",
            )
        )
        self.assertEqual(record.status, "failed")
        self.assertEqual(record.runner, "openhands")
        self.assertEqual(record.workspace_id, "workspace-1")
        self.assertEqual(record.duration_ms, 320)

        logs = asyncio.run(runner_bridge.list_logs(build_id=build.build_id))
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].log_id, record.log_id)


if __name__ == "__main__":
    unittest.main()
