"""Unit tests for runtime replanner decisions."""

from __future__ import annotations

import unittest
from uuid import uuid4

from models.builds import BuildRun, BuildStatus, DagNode, TaskRun, TaskStatus, utc_now
from orchestration.replanner import decide_runtime_replan


def _build_with_metadata(metadata: dict) -> BuildRun:
    now = utc_now()
    return BuildRun(
        build_id=uuid4(),
        created_by="user_test",
        repo_url="https://github.com/octocat/Hello-World",
        objective="replanner test",
        status=BuildStatus.running,
        created_at=now,
        updated_at=now,
        dag=[DagNode(node_id="scanner", title="scan", agent="scanner", depends_on=[])],
        metadata=metadata,
    )


def _failed_task(attempt: int) -> TaskRun:
    return TaskRun(
        task_run_id=uuid4(),
        node_id="scanner",
        attempt=attempt,
        status=TaskStatus.failed,
    )


class ReplannerTests(unittest.TestCase):
    def test_continue_when_retry_budget_available(self) -> None:
        build = _build_with_metadata({"scan_mode": "autonomous"})
        decision = decide_runtime_replan(
            build=build,
            node_id="scanner",
            task_run=_failed_task(attempt=1),
            retry_budget=1,
        )
        self.assertEqual(decision.action.value if decision.action else None, "CONTINUE")

    def test_reduce_scope_when_fallback_configured(self) -> None:
        build = _build_with_metadata(
            {
                "scan_mode": "autonomous",
                "fallback_scan_mode": "deterministic",
            }
        )
        decision = decide_runtime_replan(
            build=build,
            node_id="scanner",
            task_run=_failed_task(attempt=2),
            retry_budget=0,
        )
        self.assertEqual(decision.action.value if decision.action else None, "REDUCE_SCOPE")

    def test_abort_when_abort_policy_enabled(self) -> None:
        build = _build_with_metadata(
            {
                "scan_mode": "autonomous",
                "replanner_abort_on_terminal_failure": True,
            }
        )
        decision = decide_runtime_replan(
            build=build,
            node_id="scanner",
            task_run=_failed_task(attempt=2),
            retry_budget=0,
        )
        self.assertEqual(decision.action.value if decision.action else None, "ABORT")


if __name__ == "__main__":
    unittest.main()
