"""Runtime orchestration models for Week 1 runner gateway scaffolding."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeSession(BaseModel):
    runtime_id: UUID
    build_id: UUID
    status: Literal["bootstrapped", "running", "completed", "errored"] = "bootstrapped"
    sandbox_profile: str = "daytona-default"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata: dict = Field(default_factory=dict)


class RuntimeTickResult(BaseModel):
    build_id: UUID
    runtime_id: UUID
    executed_nodes: list[str] = Field(default_factory=list)
    pending_nodes: list[str] = Field(default_factory=list)
    finished: bool = False


class RuntimeMetric(BaseModel):
    metric: str
    build_id: UUID | None = None
    runtime_id: UUID | None = None
    value: int | float = 1
    tags: dict[str, str] = Field(default_factory=dict)
    fields: dict = Field(default_factory=dict)
    emitted_at: datetime = Field(default_factory=utc_now)


class RuntimeTelemetrySummary(BaseModel):
    build_id: UUID
    metric_count: int = 0
    bootstrap_count: int = 0
    tick_count: int = 0
    total_executed_nodes: int = 0
    latest_runtime_id: UUID | None = None
    latest_status: str | None = None
    last_emitted_at: datetime | None = None
