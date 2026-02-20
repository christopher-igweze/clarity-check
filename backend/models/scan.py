"""Pydantic models for scan requests and responses."""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ScanStatus(str, Enum):
    pending = "pending"
    scanning = "scanning"
    completed = "completed"
    failed = "failed"


class ProjectOrigin(str, Enum):
    inspired = "inspired"
    external = "external"


class SensitiveDataType(str, Enum):
    payments = "payments"
    pii = "pii"
    health = "health"
    auth_secrets = "auth_secrets"
    none = "none"
    not_sure = "not_sure"


class ProjectIntake(BaseModel):
    """Required intake context for every audit request."""

    project_origin: ProjectOrigin
    product_summary: str = Field(min_length=3, max_length=800)
    target_users: str = Field(min_length=2, max_length=400)
    sensitive_data: list[SensitiveDataType] = Field(default_factory=list)
    must_not_break_flows: list[str] = Field(default_factory=list, max_length=20)
    deployment_target: str = Field(min_length=2, max_length=200)
    scale_expectation: str = Field(min_length=2, max_length=200)


class PrimerResult(BaseModel):
    """Output contract for Agent_Primer."""

    primer_json: dict = Field(default_factory=dict)
    summary: str = ""
    repo_sha: str = ""
    confidence: int = Field(default=0, ge=0, le=100)
    failure_reason: str | None = None


class AuditRequest(BaseModel):
    """Incoming request to start an audit."""

    repo_url: HttpUrl
    vibe_prompt: str | None = None
    project_charter: dict | None = None
    project_intake: ProjectIntake
    primer: PrimerResult | None = None


class AuditResponse(BaseModel):
    """Immediate response when an audit is kicked off."""

    scan_id: UUID
    status: ScanStatus = ScanStatus.pending
    tier: str = "free"
    quota_remaining: int | None = None
    message: str = "Audit queued. Stream progress via /api/status/{scan_id}."


class FixRequest(BaseModel):
    """Request to auto-fix a specific action item."""

    action_item_id: UUID


class FixResponse(BaseModel):
    """Immediate response when an auto-fix is triggered."""

    fix_attempt_id: UUID
    status: str = "pending"
    message: str = "Fix queued. Stream progress via /api/status/{scan_id}."
