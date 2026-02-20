"""Core orchestration models for the /v1/builds control plane."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BuildStatus(str, Enum):
    pending = "pending"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"
    aborted = "aborted"


class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class ReplanAction(str, Enum):
    continue_ = "CONTINUE"
    modify_dag = "MODIFY_DAG"
    reduce_scope = "REDUCE_SCOPE"
    abort = "ABORT"


class DagNode(BaseModel):
    node_id: str
    title: str
    agent: str
    depends_on: list[str] = Field(default_factory=list)
    gate: str | None = None
    status: TaskStatus = TaskStatus.pending


class TaskRun(BaseModel):
    task_run_id: UUID
    node_id: str
    attempt: int = 1
    status: TaskStatus = TaskStatus.pending
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None
    error: str | None = None


class ReplanDecision(BaseModel):
    decision_id: UUID
    action: ReplanAction
    reason: str
    created_at: datetime = Field(default_factory=utc_now)
    replacement_nodes: list[DagNode] = Field(default_factory=list)


class DebtItem(BaseModel):
    debt_id: UUID
    node_id: str
    summary: str
    severity: str = "medium"
    created_at: datetime = Field(default_factory=utc_now)


class PolicyViolation(BaseModel):
    violation_id: UUID
    code: str
    message: str
    source: str
    blocking: bool = True
    created_at: datetime = Field(default_factory=utc_now)


class BuildEvent(BaseModel):
    event_type: str
    build_id: UUID
    timestamp: datetime = Field(default_factory=utc_now)
    payload: dict[str, Any] = Field(default_factory=dict)


class BuildCheckpoint(BaseModel):
    checkpoint_id: UUID
    build_id: UUID
    status: BuildStatus
    reason: str
    event_cursor: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class BuildRun(BaseModel):
    build_id: UUID
    created_by: str
    repo_url: str
    objective: str
    status: BuildStatus = BuildStatus.pending
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    dag: list[DagNode] = Field(default_factory=list)
    task_runs: list[TaskRun] = Field(default_factory=list)
    replan_history: list[ReplanDecision] = Field(default_factory=list)
    debt_items: list[DebtItem] = Field(default_factory=list)
    policy_violations: list[PolicyViolation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BuildRunSummary(BaseModel):
    build_id: UUID
    repo_url: str
    objective: str
    status: BuildStatus
    created_at: datetime
    updated_at: datetime


class BuildCreateRequest(BaseModel):
    repo_url: str
    objective: str = "Run autonomous code quality orchestration."
    dag: list[DagNode] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BuildCheckpointRequest(BaseModel):
    reason: str = "manual_checkpoint"
