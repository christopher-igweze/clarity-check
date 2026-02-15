"""Pydantic models for scan requests and responses."""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ScanTier(str, Enum):
    surface = "surface"
    deep = "deep"


class ScanStatus(str, Enum):
    pending = "pending"
    scanning = "scanning"
    completed = "completed"
    failed = "failed"


class AuditRequest(BaseModel):
    """Incoming request to start an audit."""

    repo_url: HttpUrl
    vibe_prompt: str | None = None
    project_charter: dict | None = None
    scan_tier: ScanTier = ScanTier.deep


class AuditResponse(BaseModel):
    """Immediate response when an audit is kicked off."""

    scan_id: UUID
    status: ScanStatus = ScanStatus.pending
    message: str = "Audit queued. Stream progress via /api/status/{scan_id}."


class FixRequest(BaseModel):
    """Request to auto-fix a specific action item."""

    action_item_id: UUID


class FixResponse(BaseModel):
    """Immediate response when an auto-fix is triggered."""

    fix_attempt_id: UUID
    status: str = "pending"
    message: str = "Fix queued. Stream progress via /api/status/{scan_id}."
