"""Program-level models for Weeks 7-16 platform delivery tracks."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ValidationCampaign(BaseModel):
    campaign_id: UUID
    name: str
    repos: list[str] = Field(default_factory=list)
    runs_per_repo: int = 3
    created_by: str
    created_at: datetime = Field(default_factory=utc_now)


class ValidationCampaignRequest(BaseModel):
    name: str
    repos: list[str] = Field(default_factory=list)
    runs_per_repo: int = 3


class CampaignRunIngestRequest(BaseModel):
    repo: str
    language: str
    run_id: str
    status: Literal["completed", "failed", "aborted"]
    duration_ms: int = 0
    findings_total: int = 0


class PolicyProfile(BaseModel):
    profile_id: UUID
    name: str
    blocked_commands: list[str] = Field(default_factory=list)
    restricted_paths: list[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=utc_now)


class PolicyProfileRequest(BaseModel):
    name: str
    blocked_commands: list[str] = Field(default_factory=list)
    restricted_paths: list[str] = Field(default_factory=list)


class PolicyCheckAction(str, Enum):
    allow = "ALLOW"
    block = "BLOCK"


class PolicyCheckRequest(BaseModel):
    profile_id: UUID
    command: str
    path: str | None = None
    build_id: UUID | None = None


class PolicyCheckResult(BaseModel):
    action: PolicyCheckAction
    reason: str
    violation_code: str | None = None


class SecretCreateRequest(BaseModel):
    name: str
    value: str


class SecretRef(BaseModel):
    secret_id: UUID
    name: str
    masked_value: str
    cipher_digest: str
    created_at: datetime = Field(default_factory=utc_now)


class SecretRecord(BaseModel):
    secret_id: UUID
    name: str
    encrypted_value: str
    created_by: str
    created_at: datetime = Field(default_factory=utc_now)


class SecretMetadata(BaseModel):
    secret_id: UUID
    name: str
    cipher_digest: str
    cipher_length: int


class PlatformWebhookRequest(BaseModel):
    payload: dict


class PlatformWebhookResponse(BaseModel):
    status: str
    nonce: str
    timestamp: int


class IdempotentCheckpointRequest(BaseModel):
    build_id: UUID
    idempotency_key: str
    reason: str = "idempotent_checkpoint"


class IdempotentCheckpointResult(BaseModel):
    checkpoint_id: UUID
    replayed: bool
    status: str
    reason: str


class SloSummary(BaseModel):
    total_builds: int
    completed_builds: int
    failed_builds: int
    aborted_builds: int
    running_builds: int
    success_rate: float
    mean_cycle_seconds: float


class ReleaseChecklist(BaseModel):
    release_id: str
    security_review: bool = False
    slo_dashboard: bool = False
    rollback_tested: bool = False
    docs_complete: bool = False
    runbooks_ready: bool = False
    updated_by: str
    updated_at: datetime = Field(default_factory=utc_now)


class ReleaseChecklistRequest(BaseModel):
    release_id: str
    security_review: bool = False
    slo_dashboard: bool = False
    rollback_tested: bool = False
    docs_complete: bool = False
    runbooks_ready: bool = False


class RollbackDrill(BaseModel):
    release_id: str
    passed: bool
    duration_minutes: int
    issues_found: list[str] = Field(default_factory=list)
    updated_by: str
    updated_at: datetime = Field(default_factory=utc_now)


class RollbackDrillRequest(BaseModel):
    release_id: str
    passed: bool
    duration_minutes: int
    issues_found: list[str] = Field(default_factory=list)


class GoLiveDecisionStatus(str, Enum):
    go = "GO"
    no_go = "NO_GO"


class GoLiveDecision(BaseModel):
    release_id: str
    status: GoLiveDecisionStatus
    reasons: list[str] = Field(default_factory=list)
    decided_by: str
    decided_at: datetime = Field(default_factory=utc_now)


class GoLiveDecisionRequest(BaseModel):
    release_id: str
    validation_release_ready: bool = False

