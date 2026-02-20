"""Open-source validation metrics helpers for Week 5 benchmarking."""

from __future__ import annotations

from math import sqrt
from typing import Literal

from pydantic import BaseModel, Field


class ValidationRun(BaseModel):
    repo: str
    language: str
    run_id: str
    status: Literal["completed", "failed", "aborted"]
    duration_ms: int = 0
    findings_total: int = 0


class RepoValidationSummary(BaseModel):
    repo: str
    language: str
    run_count: int
    success_count: int
    success_rate: float
    mean_duration_ms: float
    duration_stddev_ms: float
    duration_cv: float


class ValidationSummary(BaseModel):
    repo_count: int
    run_count: int
    avg_success_rate: float
    max_duration_cv: float
    repos: list[RepoValidationSummary] = Field(default_factory=list)


class ValidationGateResult(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)
    summary: ValidationSummary


def summarize_validation_runs(runs: list[ValidationRun]) -> ValidationSummary:
    grouped: dict[str, list[ValidationRun]] = {}
    for run in runs:
        grouped.setdefault(run.repo, []).append(run)

    repo_rows: list[RepoValidationSummary] = []
    for repo, repo_runs in sorted(grouped.items(), key=lambda item: item[0]):
        durations = [max(0, run.duration_ms) for run in repo_runs]
        duration_mean = _mean(durations)
        duration_stddev = _stddev(durations, mean=duration_mean)
        duration_cv = 0.0 if duration_mean <= 0 else duration_stddev / duration_mean
        success_count = sum(1 for run in repo_runs if run.status == "completed")
        row = RepoValidationSummary(
            repo=repo,
            language=repo_runs[0].language,
            run_count=len(repo_runs),
            success_count=success_count,
            success_rate=(success_count / len(repo_runs)) if repo_runs else 0.0,
            mean_duration_ms=duration_mean,
            duration_stddev_ms=duration_stddev,
            duration_cv=duration_cv,
        )
        repo_rows.append(row)

    run_count = len(runs)
    avg_success_rate = _mean([row.success_rate for row in repo_rows]) if repo_rows else 0.0
    max_duration_cv = max((row.duration_cv for row in repo_rows), default=0.0)
    return ValidationSummary(
        repo_count=len(repo_rows),
        run_count=run_count,
        avg_success_rate=avg_success_rate,
        max_duration_cv=max_duration_cv,
        repos=repo_rows,
    )


def evaluate_validation_gates(
    summary: ValidationSummary,
    *,
    min_success_rate: float = 0.80,
    max_duration_cv: float = 0.35,
    min_runs_per_repo: int = 3,
) -> ValidationGateResult:
    reasons: list[str] = []
    if summary.repo_count == 0:
        reasons.append("no_repositories_evaluated")

    for row in summary.repos:
        if row.run_count < min_runs_per_repo:
            reasons.append(f"insufficient_runs:{row.repo}:{row.run_count}")
        if row.success_rate < min_success_rate:
            reasons.append(f"success_rate_below_threshold:{row.repo}:{row.success_rate:.3f}")
        if row.duration_cv > max_duration_cv:
            reasons.append(f"duration_variance_above_threshold:{row.repo}:{row.duration_cv:.3f}")

    return ValidationGateResult(
        passed=len(reasons) == 0,
        reasons=reasons,
        summary=summary,
    )


def _mean(values: list[float] | list[int]) -> float:
    if not values:
        return 0.0
    return float(sum(values)) / float(len(values))


def _stddev(values: list[int], *, mean: float) -> float:
    if len(values) <= 1:
        return 0.0
    variance = sum((float(value) - mean) ** 2 for value in values) / float(len(values))
    return sqrt(variance)

