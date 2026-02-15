"""Pydantic models for audit findings and action items."""

from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Category(str, Enum):
    security = "security"
    reliability = "reliability"
    scalability = "scalability"


class FindingSource(str, Enum):
    static = "static"
    dynamic = "dynamic"


class Finding(BaseModel):
    """A single issue detected by an agent."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    category: Category
    severity: Severity
    source: FindingSource = FindingSource.static
    file_path: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    agent: str = ""


class ProbeResult(BaseModel):
    """Result of a dynamic probe step (build, test, audit, etc.)."""

    step: str
    passed: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0


class SecurityVerdict(BaseModel):
    """Security agent's validation of a finding."""

    finding_id: UUID
    confirmed: bool
    confidence: int = Field(ge=0, le=100)
    notes: str = ""


class ActionItem(BaseModel):
    """A prioritised remediation item produced by the Planner."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    category: Category
    severity: Severity
    priority: int = Field(ge=1, description="1 = highest priority")
    effort: str = "moderate"  # quick | moderate | significant
    fix_steps: list[str] = Field(default_factory=list)
    dependencies: list[UUID] = Field(default_factory=list)
    file_path: str | None = None
    line_number: int | None = None


class EducationCard(BaseModel):
    """Human-readable explanation attached to an action item."""

    action_item_id: UUID
    why_it_matters: str
    cto_perspective: str


class AuditReport(BaseModel):
    """Complete audit report assembled from all agents."""

    health_score: int = Field(ge=0, le=100)
    security_score: int = Field(ge=0, le=100)
    reliability_score: int = Field(ge=0, le=100)
    scalability_score: int = Field(ge=0, le=100)
    findings: list[Finding] = Field(default_factory=list)
    probe_results: list[ProbeResult] = Field(default_factory=list)
    security_verdicts: list[SecurityVerdict] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    education_cards: list[EducationCard] = Field(default_factory=list)
