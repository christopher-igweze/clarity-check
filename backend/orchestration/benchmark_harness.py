"""Benchmark matrix planning + reporting helpers for open-source validation."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from orchestration.validation import (
    ValidationGateResult,
    ValidationRun,
    ValidationSummary,
    evaluate_validation_gates,
    summarize_validation_runs,
)


class BenchmarkRepoTarget(BaseModel):
    repo: str
    language: str
    runs: int = Field(default=3, ge=1, le=25)


class BenchmarkRunSpec(BaseModel):
    repo: str
    language: str
    run_id: str


class BenchmarkPlan(BaseModel):
    target_count: int
    run_count: int
    runs: list[BenchmarkRunSpec] = Field(default_factory=list)


class ValidationBenchmarkReport(BaseModel):
    generated_at: datetime
    plan: BenchmarkPlan
    summary: ValidationSummary
    gate: ValidationGateResult
    rubric: BenchmarkRubric
    recommendations: list[str] = Field(default_factory=list)


class BenchmarkThresholdProfile(BaseModel):
    profile_name: str = "beta_default"
    min_repo_count: int = 10
    min_total_runs: int = 30
    min_runs_per_repo: int = 3
    min_success_rate: float = 0.80
    min_average_success_rate: float = 0.85
    max_duration_cv: float = 0.35
    release_ready_min_score: float = 85.0


class BenchmarkRubric(BaseModel):
    profile_name: str
    passed: bool
    release_ready: bool
    score: float
    reasons: list[str] = Field(default_factory=list)


def build_benchmark_plan(
    targets: list[BenchmarkRepoTarget],
    *,
    default_runs: int = 3,
) -> BenchmarkPlan:
    run_specs: list[BenchmarkRunSpec] = []
    for target in targets:
        run_count = target.runs if target.runs > 0 else default_runs
        for index in range(run_count):
            run_specs.append(
                BenchmarkRunSpec(
                    repo=target.repo,
                    language=target.language,
                    run_id=f"{_normalize_repo_name(target.repo)}-run-{index + 1}",
                )
            )
    return BenchmarkPlan(
        target_count=len(targets),
        run_count=len(run_specs),
        runs=run_specs,
    )


def compile_benchmark_report(
    runs: list[ValidationRun],
    *,
    plan: BenchmarkPlan | None = None,
    profile: BenchmarkThresholdProfile | None = None,
) -> ValidationBenchmarkReport:
    profile = profile or BenchmarkThresholdProfile()
    summary = summarize_validation_runs(runs)
    gate = evaluate_validation_gates(
        summary,
        min_success_rate=profile.min_success_rate,
        max_duration_cv=profile.max_duration_cv,
        min_runs_per_repo=profile.min_runs_per_repo,
    )
    rubric = _evaluate_benchmark_rubric(summary, gate=gate, profile=profile)
    if plan is None:
        plan = _plan_from_summary(summary)

    recommendations = _derive_recommendations(
        gate=gate,
        rubric=rubric,
        profile=profile,
    )
    return ValidationBenchmarkReport(
        generated_at=datetime.now(timezone.utc),
        plan=plan,
        summary=summary,
        gate=gate,
        rubric=rubric,
        recommendations=recommendations,
    )


def _plan_from_summary(summary: ValidationSummary) -> BenchmarkPlan:
    runs: list[BenchmarkRunSpec] = []
    for row in summary.repos:
        for index in range(row.run_count):
            runs.append(
                BenchmarkRunSpec(
                    repo=row.repo,
                    language=row.language,
                    run_id=f"{_normalize_repo_name(row.repo)}-run-{index + 1}",
                )
            )
    return BenchmarkPlan(
        target_count=summary.repo_count,
        run_count=summary.run_count,
        runs=runs,
    )


def _derive_recommendations(
    *,
    gate: ValidationGateResult,
    rubric: BenchmarkRubric,
    profile: BenchmarkThresholdProfile,
) -> list[str]:
    if rubric.release_ready:
        return ["ready_for_beta_cut"]

    recommendations: list[str] = []
    reasons = list(gate.reasons) + list(rubric.reasons)
    for reason in reasons:
        if reason.startswith("no_repositories_evaluated"):
            recommendations.append("configure_repo_targets_before_validation")
        elif reason.startswith("repo_count_below_threshold"):
            recommendations.append("expand_repo_matrix_coverage")
        elif reason.startswith("total_runs_below_threshold"):
            recommendations.append(
                f"increase_total_benchmark_runs_to_at_least_{profile.min_total_runs}"
            )
        elif reason.startswith("insufficient_runs"):
            recommendations.append(
                f"increase_runs_per_repo_to_at_least_{profile.min_runs_per_repo}"
            )
        elif reason.startswith("success_rate_below_threshold") or reason.startswith(
            "average_success_rate_below_threshold"
        ):
            recommendations.append("improve_task_success_rate_before_release")
        elif reason.startswith("duration_variance_above_threshold"):
            recommendations.append("stabilize_runtime_variance_and_retry_policies")

    return _dedupe_preserve_order(recommendations)


def _normalize_repo_name(repo: str) -> str:
    return repo.strip().replace("https://", "").replace("http://", "").replace("/", "_")


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def _evaluate_benchmark_rubric(
    summary: ValidationSummary,
    *,
    gate: ValidationGateResult,
    profile: BenchmarkThresholdProfile,
) -> BenchmarkRubric:
    reasons = list(gate.reasons)
    if summary.repo_count < profile.min_repo_count:
        reasons.append(f"repo_count_below_threshold:{summary.repo_count}")
    if summary.run_count < profile.min_total_runs:
        reasons.append(f"total_runs_below_threshold:{summary.run_count}")
    if summary.avg_success_rate < profile.min_average_success_rate:
        reasons.append(
            f"average_success_rate_below_threshold:{summary.avg_success_rate:.3f}"
        )

    score = round(_compute_score(summary, profile=profile), 2)
    reasons = _dedupe_preserve_order(reasons)
    passed = len(reasons) == 0
    release_ready = passed and score >= profile.release_ready_min_score
    return BenchmarkRubric(
        profile_name=profile.profile_name,
        passed=passed,
        release_ready=release_ready,
        score=score,
        reasons=reasons,
    )


def _compute_score(
    summary: ValidationSummary,
    *,
    profile: BenchmarkThresholdProfile,
) -> float:
    repo_ratio = _ratio(summary.repo_count, profile.min_repo_count)
    run_ratio = _ratio(summary.run_count, profile.min_total_runs)
    coverage_score = 25.0 * ((repo_ratio * 0.6) + (run_ratio * 0.4))

    success_ratio = _ratio(summary.avg_success_rate, profile.min_average_success_rate)
    success_score = 50.0 * success_ratio

    if summary.max_duration_cv <= profile.max_duration_cv:
        stability_ratio = 1.0
    else:
        overage = summary.max_duration_cv - profile.max_duration_cv
        stability_ratio = max(0.0, 1.0 - (overage / max(profile.max_duration_cv, 0.001)))
    stability_score = 25.0 * stability_ratio

    return coverage_score + success_score + stability_score


def _ratio(value: float | int, baseline: float | int) -> float:
    if baseline <= 0:
        return 1.0
    return max(0.0, min(float(value) / float(baseline), 1.0))
