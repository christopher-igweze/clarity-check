"""Tests for open-source validation summary and gate evaluation."""

from __future__ import annotations

import unittest

from orchestration.validation import (
    ValidationRun,
    evaluate_validation_gates,
    evaluate_validation_rubric,
    ValidationThresholdProfile,
    summarize_validation_runs,
)


class ValidationMetricsTests(unittest.TestCase):
    @staticmethod
    def _make_high_quality_runs(repo_count: int = 10, runs_per_repo: int = 3) -> list[ValidationRun]:
        runs: list[ValidationRun] = []
        for repo_idx in range(repo_count):
            repo_name = f"repo-{repo_idx:02d}"
            language = "python" if repo_idx % 2 == 0 else "node"
            for run_idx in range(runs_per_repo):
                runs.append(
                    ValidationRun(
                        repo=repo_name,
                        language=language,
                        run_id=f"{repo_name}-run-{run_idx}",
                        status="completed",
                        duration_ms=1200 + (repo_idx * 10) + run_idx,
                    )
                )
        return runs

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

    def test_evaluate_validation_rubric_marks_release_ready(self) -> None:
        runs = self._make_high_quality_runs(repo_count=10, runs_per_repo=3)
        summary = summarize_validation_runs(runs)

        rubric = evaluate_validation_rubric(summary)
        self.assertTrue(rubric.passed)
        self.assertTrue(rubric.release_ready)
        self.assertGreaterEqual(rubric.score, 90.0)
        self.assertEqual(rubric.reasons, [])

    def test_evaluate_validation_rubric_flags_coverage_and_success_gaps(self) -> None:
        runs = [
            ValidationRun(repo="repo-a", language="python", run_id="a1", status="completed", duration_ms=1000),
            ValidationRun(repo="repo-a", language="python", run_id="a2", status="failed", duration_ms=4200),
            ValidationRun(repo="repo-b", language="node", run_id="b1", status="completed", duration_ms=1000),
        ]
        summary = summarize_validation_runs(runs)

        rubric = evaluate_validation_rubric(
            summary,
            profile=ValidationThresholdProfile(
                min_repo_count=3,
                min_total_runs=9,
                min_runs_per_repo=3,
                min_success_rate=0.8,
                min_average_success_rate=0.85,
                max_duration_cv=0.2,
                release_ready_min_score=85.0,
            ),
        )
        self.assertFalse(rubric.passed)
        self.assertFalse(rubric.release_ready)
        self.assertLess(rubric.score, 85.0)
        self.assertTrue(any(reason.startswith("repo_count_below_threshold:") for reason in rubric.reasons))
        self.assertTrue(any(reason.startswith("total_runs_below_threshold:") for reason in rubric.reasons))
        self.assertTrue(any(reason.startswith("average_success_rate_below_threshold:") for reason in rubric.reasons))


if __name__ == "__main__":
    unittest.main()
