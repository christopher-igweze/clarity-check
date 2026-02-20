"""Tests for benchmark harness planning and validation report generation."""

from __future__ import annotations

import unittest

from orchestration.benchmark_harness import (
    BenchmarkRepoTarget,
    build_benchmark_plan,
    compile_benchmark_report,
)
from orchestration.validation import ValidationRun


class BenchmarkHarnessTests(unittest.TestCase):
    def test_build_benchmark_plan_generates_deterministic_run_specs(self) -> None:
        plan = build_benchmark_plan(
            [
                BenchmarkRepoTarget(repo="https://github.com/org/repo-a", language="python", runs=2),
                BenchmarkRepoTarget(repo="github.com/org/repo-b", language="node", runs=1),
            ]
        )
        self.assertEqual(plan.target_count, 2)
        self.assertEqual(plan.run_count, 3)
        run_ids = [row.run_id for row in plan.runs]
        self.assertEqual(
            run_ids,
            [
                "github.com_org_repo-a-run-1",
                "github.com_org_repo-a-run-2",
                "github.com_org_repo-b-run-1",
            ],
        )

    def test_compile_benchmark_report_includes_recommendations(self) -> None:
        runs = [
            ValidationRun(repo="repo-a", language="python", run_id="a1", status="completed", duration_ms=1000),
            ValidationRun(repo="repo-a", language="python", run_id="a2", status="failed", duration_ms=3000),
            ValidationRun(repo="repo-b", language="node", run_id="b1", status="completed", duration_ms=1000),
        ]
        report = compile_benchmark_report(runs)
        self.assertFalse(report.rubric.release_ready)
        self.assertGreater(len(report.recommendations), 0)
        self.assertTrue(
            any(
                recommendation.startswith("increase_total_benchmark_runs_to_at_least_")
                for recommendation in report.recommendations
            )
        )

    def test_compile_benchmark_report_marks_ready_for_beta_cut(self) -> None:
        runs: list[ValidationRun] = []
        for repo_idx in range(10):
            repo = f"repo-{repo_idx:02d}"
            language = "python" if repo_idx % 2 == 0 else "node"
            for run_idx in range(3):
                runs.append(
                    ValidationRun(
                        repo=repo,
                        language=language,
                        run_id=f"{repo}-run-{run_idx}",
                        status="completed",
                        duration_ms=1000 + repo_idx + run_idx,
                    )
                )
        report = compile_benchmark_report(runs)
        self.assertTrue(report.rubric.release_ready)
        self.assertEqual(report.recommendations, ["ready_for_beta_cut"])


if __name__ == "__main__":
    unittest.main()

