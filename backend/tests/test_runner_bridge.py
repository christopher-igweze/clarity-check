"""Unit tests for runner bridge normalization and log recording."""

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

    def test_execute_daytona_shell_runner_uses_daytona_command_layer(self) -> None:
        build = _build_with_overrides("completed")
        build.metadata["runner_kind"] = "daytona_shell"
        build.metadata["runner_results"]["scanner"]["command"] = "echo hello"
        runtime_id = uuid4()

        with patch.object(
            runner_bridge,
            "_run_daytona_command",
            new=AsyncMock(return_value=("ws-daytona-99", 0, "hello", "")),
        ):
            record = asyncio.run(
                runner_bridge.execute(
                    build=build,
                    runtime_id=runtime_id,
                    node_id="scanner",
                )
            )
        self.assertEqual(record.runner, "daytona_shell")
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.workspace_id, "ws-daytona-99")
        self.assertEqual(record.metadata.get("execution_mode"), "daytona_shell")
        self.assertEqual(record.metadata.get("command"), "echo hello")

    def test_execute_openhands_daytona_runner_parses_result_payload(self) -> None:
        build = _build_with_overrides("completed")
        build.metadata["runner_kind"] = "openhands_daytona"
        build.metadata["runner_results"]["scanner"]["prompt"] = "Audit node"
        runtime_id = uuid4()

        class _FakeManager:
            async def upload_file(self, scan_id, path, content):
                return None

            async def read_file(self, scan_id, path):
                return '{"status":"completed","summary":"node done","notes":"ok"}'

        fake_manager = _FakeManager()
        with (
            patch.object(runner_bridge, "_get_sandbox_manager", return_value=fake_manager),
            patch.object(runner_bridge, "_ensure_openhands_daytona_runtime", new=AsyncMock(return_value=None)),
            patch.object(
                runner_bridge,
                "_run_daytona_command",
                new=AsyncMock(return_value=("ws-openhands-1", 0, "stdout", "")),
            ),
        ):
            record = asyncio.run(
                runner_bridge.execute(
                    build=build,
                    runtime_id=runtime_id,
                    node_id="scanner",
                )
            )
        self.assertEqual(record.runner, "openhands_daytona")
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.workspace_id, "ws-openhands-1")
        self.assertEqual(record.message, "node done")
        self.assertEqual(record.metadata.get("execution_mode"), "openhands_daytona")

    def test_execute_blocks_daytona_command_on_policy_violation(self) -> None:
        build = _build_with_overrides("completed")
        build.metadata["runner_kind"] = "daytona_shell"
        build.metadata["runner_results"]["scanner"]["command"] = "git reset --hard HEAD"
        runtime_id = uuid4()

        run_daytona = AsyncMock(return_value=("ws-daytona-99", 0, "ok", ""))
        with patch.object(runner_bridge, "_run_daytona_command", new=run_daytona):
            record = asyncio.run(
                runner_bridge.execute(
                    build=build,
                    runtime_id=runtime_id,
                    node_id="scanner",
                )
            )
        self.assertEqual(record.status, "failed")
        self.assertEqual(record.metadata.get("execution_mode"), "policy_precheck")
        violation = record.metadata.get("policy_violation", {})
        self.assertEqual(violation.get("code"), "blocked_command")
        run_daytona.assert_not_awaited()

    def test_execute_blocks_when_required_capability_missing(self) -> None:
        build = _build_with_overrides("completed")
        build.metadata["runner_kind"] = "daytona_shell"
        build.metadata["runner_results"]["scanner"]["command"] = "echo safe"
        build.metadata["node_policy"] = {
            "scanner": {"required_capabilities": ["runtime.execute"]}
        }
        build.metadata["executor_capabilities"] = ["runtime.read"]
        runtime_id = uuid4()

        run_daytona = AsyncMock(return_value=("ws-daytona-99", 0, "ok", ""))
        with patch.object(runner_bridge, "_run_daytona_command", new=run_daytona):
            record = asyncio.run(
                runner_bridge.execute(
                    build=build,
                    runtime_id=runtime_id,
                    node_id="scanner",
                )
            )
        self.assertEqual(record.status, "failed")
        violation = record.metadata.get("policy_violation", {})
        self.assertEqual(violation.get("code"), "missing_capability")
        run_daytona.assert_not_awaited()

    def test_finalize_build_destroys_active_daytona_workspace(self) -> None:
        class _FakeManager:
            def __init__(self) -> None:
                self.destroyed: list = []

            async def destroy(self, build_id):
                self.destroyed.append(build_id)

        fake_manager = _FakeManager()
        build_id = uuid4()
        original_manager = runner_bridge._sandbox_manager
        try:
            runner_bridge._sandbox_manager = fake_manager
            runner_bridge._active_daytona_workspaces[build_id] = "ws-daytona-1"

            asyncio.run(runner_bridge.finalize_build(build_id))
            self.assertEqual(fake_manager.destroyed, [build_id])
            self.assertNotIn(build_id, runner_bridge._active_daytona_workspaces)
        finally:
            runner_bridge._sandbox_manager = original_manager


if __name__ == "__main__":
    unittest.main()
