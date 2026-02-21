"""Runtime routes for Week 1 runner gateway scaffolding."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from api.middleware.rate_limit import limiter, rate_limit_string
from config import settings
from models.builds import BuildStatus
from models.runtime import (
    RuntimeMetric,
    RuntimeRunLog,
    RuntimeSession,
    RuntimeWorkerHealth,
    RuntimeTelemetrySummary,
    RuntimeTickResult,
)
from orchestration.runner_bridge import runner_bridge
from orchestration.runtime_gateway import runtime_gateway
from orchestration.store import build_store
from orchestration.runtime_tick import execute_runtime_tick
from orchestration.telemetry import list_runtime_metrics, summarize_runtime_metrics

router = APIRouter()

_WORKER_LIVENESS_EVENTS = {
    "RUNTIME_BOOTSTRAPPED",
    "LEVEL_STARTED",
    "TASK_STARTED",
    "TASK_COMPLETED",
    "TASK_FAILED",
    "RUNNER_RESULT",
    "TASK_RETRY_SCHEDULED",
    "FALLBACK_MODE_SWITCHED",
    "BUILD_STATUS_CHANGED",
    "BUILD_FINISHED",
}


async def _get_owned_build(request: Request, build_id: UUID):
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


@router.post("/v1/builds/{build_id}/runtime/bootstrap", response_model=RuntimeSession)
@limiter.limit(rate_limit_string())
async def bootstrap_runtime(build_id: UUID, request: Request) -> RuntimeSession:
    build = await _get_owned_build(request, build_id)
    session = await runtime_gateway.bootstrap(build)
    session.metadata = {
        **(session.metadata or {}),
        "runtime_worker_enabled": settings.runtime_worker_enabled,
        "runtime_client_tick_fallback_enabled": settings.runtime_client_tick_fallback_enabled,
        "runtime_watchdog_nudge_enabled": settings.runtime_watchdog_nudge_enabled,
        "runtime_watchdog_stale_seconds": settings.runtime_watchdog_stale_seconds,
    }
    await build_store.append_event(
        build_id,
        event_type="RUNTIME_BOOTSTRAPPED",
        payload={
            "runtime_id": str(session.runtime_id),
            "status": session.status,
            "runtime_worker_enabled": settings.runtime_worker_enabled,
        },
    )
    return session


@router.get("/v1/builds/{build_id}/runtime/worker-health", response_model=RuntimeWorkerHealth)
async def runtime_worker_health(build_id: UUID, request: Request) -> RuntimeWorkerHealth:
    build = await _get_owned_build(request, build_id)
    stale_after_seconds = max(10, int(settings.runtime_watchdog_stale_seconds))
    last_runtime_event_at: datetime | None = None
    events = await build_store.list_events(build_id)
    for event in reversed(events):
        if event.event_type in _WORKER_LIVENESS_EVENTS:
            last_runtime_event_at = event.timestamp
            break

    reference_time = last_runtime_event_at or build.updated_at
    worker_stale = False
    if settings.runtime_worker_enabled and build.status == BuildStatus.running:
        age = (datetime.now(timezone.utc) - reference_time).total_seconds()
        worker_stale = age >= stale_after_seconds

    nudge_allowed = bool(
        settings.runtime_worker_enabled
        and settings.runtime_watchdog_nudge_enabled
        and worker_stale
        and build.status == BuildStatus.running
    )
    return RuntimeWorkerHealth(
        build_id=build_id,
        worker_enabled=settings.runtime_worker_enabled,
        worker_stale=worker_stale,
        nudge_allowed=nudge_allowed,
        stale_after_seconds=stale_after_seconds,
        last_runtime_event_at=last_runtime_event_at,
    )


@router.get("/v1/builds/{build_id}/runtime/status", response_model=RuntimeSession)
async def runtime_status(build_id: UUID, request: Request) -> RuntimeSession:
    await _get_owned_build(request, build_id)
    session = await runtime_gateway.get_session(build_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "runtime_not_found", "message": "Runtime session not found."},
        )
    return session


@router.get("/v1/builds/{build_id}/runtime/metrics", response_model=list[RuntimeMetric])
async def runtime_metrics(
    build_id: UUID,
    request: Request,
    metric: str | None = None,
    limit: int = 200,
) -> list[RuntimeMetric]:
    await _get_owned_build(request, build_id)
    return await list_runtime_metrics(
        build_id=build_id,
        metric=metric,
        limit=limit,
    )


@router.get("/v1/builds/{build_id}/runtime/telemetry", response_model=RuntimeTelemetrySummary)
async def runtime_telemetry(build_id: UUID, request: Request) -> RuntimeTelemetrySummary:
    await _get_owned_build(request, build_id)
    return await summarize_runtime_metrics(build_id)


@router.get("/v1/builds/{build_id}/runtime/logs", response_model=list[RuntimeRunLog])
async def runtime_logs(
    build_id: UUID,
    request: Request,
    node_id: str | None = None,
    status: str | None = None,
    limit: int = 200,
) -> list[RuntimeRunLog]:
    await _get_owned_build(request, build_id)
    return await runner_bridge.list_logs(
        build_id=build_id,
        node_id=node_id,
        status=status,
        limit=limit,
    )


@router.post("/v1/builds/{build_id}/runtime/tick", response_model=RuntimeTickResult)
@limiter.limit(rate_limit_string())
async def runtime_tick(build_id: UUID, request: Request) -> RuntimeTickResult:
    await _get_owned_build(request, build_id)
    try:
        return await execute_runtime_tick(build_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "runtime_tick_conflict", "message": str(exc)},
        ) from exc
