"""Tests for open-source validation summary and gate evaluation."""

from __future__ import annotations

import unittest

from orchestration.validation import (
    ValidationRun,
    evaluate_validation_gates,
    summarize_validation_runs,
)


class ValidationMetricsTests(unittest.TestCase):
    def test_summarize_validation_runs_computes_repo_metrics(self) -> None:
        runs = [
            ValidationRun(repo="repo-a", language="python", run_id="a1", status="completed", duration_ms=1000),
            ValidationRun(repo="repo-a", language="python", run_id="a2", status="completed", duration_ms=1200),
            ValidationRun(repo="repo-a", language="python", run_id="a3", status="failed", duration_ms=1300),
            ValidationRun(repo="repo-b", language="node", run_id="b1", status="completed", duration_ms=900),
            ValidationRun(repo="repo-b", language="node", run_id="b2", status="completed", duration_ms=920),
            ValidationRun(repo="repo-b", language="node", run_id="b3", status="completed", duration_ms=940),
        ]

        summary = summarize_validation_runs(runs)
        self.assertEqual(summary.repo_count, 2)
        self.assertEqual(summary.run_count, 6)
        self.assertGreater(summary.avg_success_rate, 0.80)
        self.assertGreaterEqual(summary.max_duration_cv, 0.0)

        repo_a = next(row for row in summary.repos if row.repo == "repo-a")
        self.assertEqual(repo_a.run_count, 3)
        self.assertEqual(repo_a.success_count, 2)
        self.assertAlmostEqual(repo_a.success_rate, 2 / 3, places=5)

    def test_evaluate_validation_gates_flags_threshold_violations(self) -> None:
        runs = [
            ValidationRun(repo="repo-a", language="python", run_id="a1", status="failed", duration_ms=500),
            ValidationRun(repo="repo-a", language="python", run_id="a2", status="completed", duration_ms=5000),
            ValidationRun(repo="repo-b", language="node", run_id="b1", status="completed", duration_ms=1000),
            ValidationRun(repo="repo-b", language="node", run_id="b2", status="completed", duration_ms=1000),
        ]
        summary = summarize_validation_runs(runs)
        gate = evaluate_validation_gates(summary, min_success_rate=0.8, max_duration_cv=0.2, min_runs_per_repo=3)
        self.assertFalse(gate.passed)
        self.assertTrue(any(reason.startswith("success_rate_below_threshold:repo-a") for reason in gate.reasons))
        self.assertTrue(any(reason.startswith("insufficient_runs:repo-b") for reason in gate.reasons))


if __name__ == "__main__":
    unittest.main()

