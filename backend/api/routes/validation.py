"""Validation planning/reporting endpoints for open-source benchmark runs."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter, rate_limit_string
from orchestration.benchmark_harness import (
    BenchmarkPlan,
    BenchmarkRepoTarget,
    BenchmarkThresholdProfile,
    ValidationBenchmarkReport,
    build_benchmark_plan,
    compile_benchmark_report,
)
from orchestration.validation import ValidationRun

router = APIRouter()


class ValidationPlanRequest(BaseModel):
    targets: list[BenchmarkRepoTarget] = Field(default_factory=list)
    default_runs: int = Field(default=3, ge=1, le=25)


class ValidationReportRequest(BaseModel):
    runs: list[ValidationRun] = Field(default_factory=list)
    profile: BenchmarkThresholdProfile | None = None


@router.post("/v1/validation/plan", response_model=BenchmarkPlan)
@limiter.limit(rate_limit_string())
async def build_validation_plan(
    request_body: ValidationPlanRequest,
    request: Request,
) -> BenchmarkPlan:
    _ = request.state.user_id
    return build_benchmark_plan(
        request_body.targets,
        default_runs=request_body.default_runs,
    )


@router.post("/v1/validation/report", response_model=ValidationBenchmarkReport)
@limiter.limit(rate_limit_string())
async def build_validation_report(
    request_body: ValidationReportRequest,
    request: Request,
) -> ValidationBenchmarkReport:
    _ = request.state.user_id
    return compile_benchmark_report(
        request_body.runs,
        profile=request_body.profile,
    )
