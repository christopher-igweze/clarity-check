"""Unit tests for Daytona OpenHands matrix scoring and capacity helpers."""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_daytona_openhands_fix_matrix.py"
)
spec = importlib.util.spec_from_file_location("matrix_runner", SCRIPT_PATH)
assert spec and spec.loader
matrix_runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = matrix_runner
spec.loader.exec_module(matrix_runner)


class DaytonaOpenHandsMatrixTests(unittest.TestCase):
    def test_resource_worker_cap_supports_nine_parallel(self) -> None:
        cap = matrix_runner.compute_resource_worker_cap(
            pool_cpu=10,
            pool_memory_gb=10,
            pool_storage_gb=30,
            sandbox_cpu=1,
            sandbox_memory_gb=1,
            sandbox_disk_gb=3,
        )
        self.assertGreaterEqual(cap, 9)

    def test_choose_first_healthy_medium_freezes_first_healthy(self) -> None:
        rows = [
            {"repo": {"label": "first"}, "ok": False},
            {"repo": {"label": "second"}, "ok": True},
            {"repo": {"label": "third"}, "ok": True},
        ]
        selected = matrix_runner.choose_first_healthy_medium(rows)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["repo"]["label"], "second")

    def test_score_run_enforces_hard_gate_for_c1_and_c5(self) -> None:
        scored = matrix_runner.score_run(
            before_actionable=4,
            after_actionable=2,
            baseline_tests_exit=0,
            post_tests_exit=0,
            before_findings=[{"severity": "high"}],
            after_findings=[{"severity": "medium"}],
            final_response="Can you clarify expected behavior?",
            final_response_json={
                "asked_follow_up_questions": True,
                "user_summary": "done",
                "branch_name": "codex/demo-fix-1",
                "implementation_doc": "docs/agent-implementation-note.md",
            },
            changed_files=["src/app.py"],
            score_target=85.0,
            active_branch="codex/demo-fix-1",
            implementation_doc_exists=True,
        )

        self.assertEqual(scored["criteria"]["c1_one_shot_compliance"], 0.0)
        self.assertTrue(scored["hard_gate_failed"])
        self.assertFalse(scored["passed"])


if __name__ == "__main__":
    unittest.main()
