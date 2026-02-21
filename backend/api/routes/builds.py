"""Week 1 orchestration control-plane routes."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from api.middleware.rate_limit import limiter, rate_limit_string
from models.builds import (
    BuildCheckpoint,
    BuildCheckpointRequest,
    BuildCreateRequest,
    BuildDagPreview,
    BuildEvent,
    BuildGateDecisionRequest,
    BuildRun,
    BuildRunSummary,
    DebtItem,
    DebtItemRequest,
    GateDecision,
    GateType,
    PolicyViolation,
    PolicyViolationRequest,
    ReplanDecision,
    ReplanDecisionRequest,
    ReplanSuggestion,
    ReplanSuggestionApplyRequest,
    TaskRun,
    TaskRunCompleteRequest,
    TaskRunStartRequest,
    TaskStatus,
    BuildStatus,
)
from orchestration.prompt_contracts import list_prompt_contracts
from orchestration.store import build_store

router = APIRouter()


class BuildActionRequest(BaseModel):
    reason: str | None = None


async def _get_owned_build(request: Request, build_id: UUID) -> BuildRun:
    user_id: str = request.state.user_id
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    if build.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "build_access_denied",
                "message": "You do not have access to this build.",
            },
        )
    return build


@router.get("/v1/builds", response_model=list[BuildRunSummary])
async def list_builds(
    request: Request,
    status: BuildStatus | None = None,
    limit: int = 20,
) -> list[BuildRunSummary]:
    user_id: str = request.state.user_id
    return await build_store.list_builds(
        user_id=user_id,
        status=status,
        limit=limit,
    )


@router.post("/v1/builds/preview-dag", response_model=BuildDagPreview)
@limiter.limit(rate_limit_string())
async def preview_build_dag(
    request_body: BuildCreateRequest,
    request: Request,
) -> BuildDagPreview:
    _ = request.state.user_id
    try:
        return await build_store.preview_build_dag(request_body)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_dag", "message": str(exc)},
        ) from exc


@router.post("/v1/builds", response_model=BuildRun)
@limiter.limit(rate_limit_string())
async def create_build(
    request_body: BuildCreateRequest,
    request: Request,
) -> BuildRun:
    user_id: str = request.state.user_id
    try:
        return await build_store.create_build(user_id=user_id, request=request_body)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_dag", "message": str(exc)},
        ) from exc


@router.get("/v1/builds/{build_id}", response_model=BuildRun)
async def get_build(build_id: UUID, request: Request) -> BuildRun:
    return await _get_owned_build(request, build_id)


@router.get("/v1/builds/{build_id}/tasks", response_model=list[TaskRun])
async def list_task_runs(
    build_id: UUID,
    request: Request,
    node_id: str | None = None,
    status: TaskStatus | None = None,
    limit: int = 200,
) -> list[TaskRun]:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.list_task_runs(
            build_id,
            node_id=node_id,
            status=status,
            limit=limit,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.get("/v1/builds/{build_id}/tasks/{task_run_id}", response_model=TaskRun)
async def get_task_run(build_id: UUID, task_run_id: UUID, request: Request) -> TaskRun:
    await _get_owned_build(request, build_id)
    try:
        task_run = await build_store.get_task_run(build_id, task_run_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    if task_run is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "task_run_not_found", "message": "Task run not found."},
        )
    return task_run


@router.post("/v1/builds/{build_id}/tasks", response_model=TaskRun)
@limiter.limit(rate_limit_string())
async def start_task_run(
    build_id: UUID,
    request_body: TaskRunStartRequest,
    request: Request,
) -> TaskRun:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.start_task_run(
            build_id,
            node_id=request_body.node_id,
            source="manual",
        )
    except KeyError as exc:
        code = str(exc)
        if "dag_node_not_found" in code:
            raise HTTPException(
                status_code=404,
                detail={"code": "dag_node_not_found", "message": "DAG node not found."},
            ) from exc
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "task_run_conflict", "message": str(exc)},
        ) from exc


@router.post("/v1/builds/{build_id}/tasks/{task_run_id}/complete", response_model=TaskRun)
@limiter.limit(rate_limit_string())
async def complete_task_run(
    build_id: UUID,
    task_run_id: UUID,
    request_body: TaskRunCompleteRequest,
    request: Request,
) -> TaskRun:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.complete_task_run(
            build_id,
            task_run_id=task_run_id,
            status=request_body.status,
            error=request_body.error,
            source="manual",
        )
    except KeyError as exc:
        code = str(exc)
        if "task_run_not_found" in code:
            raise HTTPException(
                status_code=404,
                detail={"code": "task_run_not_found", "message": "Task run not found."},
            ) from exc
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "task_run_conflict", "message": str(exc)},
        ) from exc


@router.get("/v1/builds/{build_id}/gates", response_model=list[GateDecision])
async def list_gate_decisions(
    build_id: UUID,
    request: Request,
    gate: GateType | None = None,
    limit: int = 200,
) -> list[GateDecision]:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.list_gate_decisions(
            build_id,
            gate=gate,
            limit=limit,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.post("/v1/builds/{build_id}/gates/{gate}", response_model=GateDecision)
@limiter.limit(rate_limit_string())
async def record_gate_decision(
    build_id: UUID,
    gate: GateType,
    request_body: BuildGateDecisionRequest,
    request: Request,
) -> GateDecision:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.record_gate_decision(
            build_id,
            gate=gate,
            status=request_body.status,
            reason=request_body.reason,
            node_id=request_body.node_id,
            source="manual",
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.get("/v1/builds/{build_id}/replan", response_model=list[ReplanDecision])
async def list_replan_decisions(
    build_id: UUID,
    request: Request,
    limit: int = 200,
) -> list[ReplanDecision]:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.list_replan_decisions(build_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.post("/v1/builds/{build_id}/replan", response_model=ReplanDecision)
@limiter.limit(rate_limit_string())
async def record_replan_decision(
    build_id: UUID,
    request_body: ReplanDecisionRequest,
    request: Request,
) -> ReplanDecision:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.record_replan_decision(
            build_id,
            action=request_body.action,
            reason=request_body.reason,
            replacement_nodes=request_body.replacement_nodes,
            source="manual",
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_replan", "message": str(exc)},
        ) from exc


@router.get("/v1/builds/{build_id}/replan/suggest", response_model=ReplanSuggestion)
async def suggest_replan_decision(build_id: UUID, request: Request) -> ReplanSuggestion:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.suggest_replan_decision(build_id, source="debt_triage")
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.post("/v1/builds/{build_id}/replan/suggest/apply", response_model=ReplanDecision)
@limiter.limit(rate_limit_string())
async def apply_suggested_replan_decision(
    build_id: UUID,
    request_body: ReplanSuggestionApplyRequest,
    request: Request,
) -> ReplanDecision:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.apply_suggested_replan(
            build_id,
            reason_override=request_body.reason,
            source="debt_triage",
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_replan", "message": str(exc)},
        ) from exc


@router.get("/v1/builds/{build_id}/debt", response_model=list[DebtItem])
async def list_debt_items(
    build_id: UUID,
    request: Request,
    limit: int = 200,
) -> list[DebtItem]:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.list_debt_items(build_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.post("/v1/builds/{build_id}/debt", response_model=DebtItem)
@limiter.limit(rate_limit_string())
async def record_debt_item(
    build_id: UUID,
    request_body: DebtItemRequest,
    request: Request,
) -> DebtItem:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.record_debt_item(
            build_id,
            node_id=request_body.node_id,
            summary=request_body.summary,
            severity=request_body.severity,
            source="manual",
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.get("/v1/builds/{build_id}/policy-violations", response_model=list[PolicyViolation])
async def list_policy_violations(
    build_id: UUID,
    request: Request,
    limit: int = 200,
) -> list[PolicyViolation]:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.list_policy_violations(build_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.post("/v1/builds/{build_id}/policy-violations", response_model=PolicyViolation)
@limiter.limit(rate_limit_string())
async def record_policy_violation(
    build_id: UUID,
    request_body: PolicyViolationRequest,
    request: Request,
) -> PolicyViolation:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.record_policy_violation(
            build_id,
            code=request_body.code,
            message=request_body.message,
            source=request_body.source,
            blocking=request_body.blocking,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.post("/v1/builds/{build_id}/resume", response_model=BuildRun)
@limiter.limit(rate_limit_string())
async def resume_build(
    build_id: UUID,
    request_body: BuildActionRequest,
    request: Request,
) -> BuildRun:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.resume_build(build_id, reason=request_body.reason)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "build_resume_conflict",
                "message": str(exc),
            },
        ) from exc


@router.post("/v1/builds/{build_id}/abort", response_model=BuildRun)
@limiter.limit(rate_limit_string())
async def abort_build(
    build_id: UUID,
    request_body: BuildActionRequest,
    request: Request,
) -> BuildRun:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.abort_build(build_id, reason=request_body.reason)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "build_abort_conflict",
                "message": str(exc),
            },
        ) from exc


async def _build_event_generator(build_id: UUID):
    cursor = 0
    idle_ticks = 0
    max_idle = 300

    while True:
        events = await build_store.list_events(build_id)
        build = await build_store.get_build(build_id)
        if build is None:
            yield {
                "event": "error",
                "data": json.dumps({"code": "build_not_found", "message": "Build not found."}),
            }
            return

        if cursor < len(events):
            for entry in events[cursor:]:
                yield {
                    "event": entry.event_type,
                    "data": json.dumps(entry.model_dump(mode="json"), default=str),
                }
            cursor = len(events)
            idle_ticks = 0
        else:
            idle_ticks += 1

        if build.status in (
            BuildStatus.completed,
            BuildStatus.failed,
            BuildStatus.aborted,
        ) and cursor >= len(events):
            return

        if idle_ticks >= max_idle:
            yield {
                "event": "timeout",
                "data": json.dumps({"message": "Build event stream timed out."}),
            }
            return

        await asyncio.sleep(1)


@router.get("/v1/builds/{build_id}/events")
async def stream_build_events(build_id: UUID, request: Request) -> EventSourceResponse:
    await _get_owned_build(request, build_id)
    return EventSourceResponse(
        _build_event_generator(build_id),
        media_type="text/event-stream",
    )


@router.get("/v1/builds/{build_id}/events/history", response_model=list[BuildEvent])
async def list_build_events_history(
    build_id: UUID,
    request: Request,
    cursor: int = 0,
    limit: int = 500,
) -> list[BuildEvent]:
    await _get_owned_build(request, build_id)
    safe_cursor = max(0, cursor)
    safe_limit = max(1, min(limit, 2000))
    events = await build_store.list_events(build_id)
    return events[safe_cursor : safe_cursor + safe_limit]


@router.get("/v1/builds/{build_id}/checkpoints", response_model=list[BuildCheckpoint])
async def list_build_checkpoints(build_id: UUID, request: Request) -> list[BuildCheckpoint]:
    await _get_owned_build(request, build_id)
    return await build_store.list_checkpoints(build_id)


@router.post("/v1/builds/{build_id}/checkpoints", response_model=BuildCheckpoint)
@limiter.limit(rate_limit_string())
async def create_build_checkpoint(
    build_id: UUID,
    request_body: BuildCheckpointRequest,
    request: Request,
) -> BuildCheckpoint:
    await _get_owned_build(request, build_id)
    try:
        return await build_store.create_checkpoint(
            build_id,
            reason=request_body.reason,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc


@router.get("/v1/prompt-contracts")
async def get_prompt_contracts() -> list[dict]:
    """Expose current prompt contract registry for build/runtime alignment."""
    return [contract.__dict__ for contract in list_prompt_contracts()]
