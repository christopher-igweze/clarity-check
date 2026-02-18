"""Contracts for Tier 1 deterministic scan and report pipeline."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class Tier1Evidence(BaseModel):
    file_path: str
    line_number: int | None = None
    snippet: str = ""
    match: str = ""


class Tier1Finding(BaseModel):
    check_id: str
    status: str  # pass | warn | fail
    category: str  # security | reliability | scalability
    severity: str  # critical | high | medium | low
    engine: str  # index | ast | linter | regex | hybrid
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    title: str
    description: str
    evidence: list[Tier1Evidence] = Field(default_factory=list)
    suggested_fix_stub: str


class Tier1ScanResult(BaseModel):
    repo_sha: str
    cache_hit: bool = False
    loc_total: int = 0
    file_count: int = 0
    findings: list[Tier1Finding] = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)


class Tier1ReportArtifact(BaseModel):
    markdown: str
    agent_markdown: str = ""
    pdf_base64: str | None = None
    summary_json: dict = Field(default_factory=dict)
    expires_at: datetime
    model_used: str | None = None
    fallback_used: bool = False


class Tier1QuotaStatus(BaseModel):
    tier: str = "free"
    month_key: date
    reports_generated: int
    reports_limit: int
    reports_remaining: int
    project_count: int
    project_limit: int
    loc_cap: int
