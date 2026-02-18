"""Pydantic models for agent log events streamed to the frontend."""

from __future__ import annotations

from enum import Enum
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    info = "info"
    warn = "warn"
    error = "error"
    success = "success"


class AgentName(str, Enum):
    primer = "Agent_Primer"
    scanner = "Agent_Scanner"
    evolution = "Agent_Evolution"
    builder = "Agent_Builder"
    security = "Agent_Security"
    planner = "Agent_Planner"
    educator = "Agent_Educator"
    implementer = "Agent_Implementer"
    verifier = "Agent_Verifier"
    orchestrator = "Orchestrator"


class SSEEventType(str, Enum):
    """Event types sent over the SSE stream."""

    agent_start = "agent_start"
    agent_log = "agent_log"
    agent_complete = "agent_complete"
    finding = "finding"
    probe_result = "probe_result"
    security_verdict = "security_verdict"
    action_item = "action_item"
    education_card = "education_card"
    scan_complete = "scan_complete"
    scan_error = "scan_error"


class AgentLogEntry(BaseModel):
    """A single log line from an agent, streamed to the UI."""

    event_type: SSEEventType
    agent: AgentName
    message: str
    level: LogLevel = LogLevel.info
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict | None = None
