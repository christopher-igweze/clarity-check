"""Runtime routes for Week 1 runner gateway scaffolding."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from api.middleware.rate_limit import limiter, rate_limit_string
from models.builds import BuildStatus, GateDecisionStatus, TaskStatus
from models.runtime import RuntimeSession, RuntimeTickResult
from orchestration.runtime_gateway import runtime_gateway
from orchestration.store import build_store

router = APIRouter()


@router.post("/v1/builds/{build_id}/runtime/bootstrap", response_model=RuntimeSession)
@limiter.limit(rate_limit_string())
async def bootstrap_runtime(build_id: UUID, request: Request) -> RuntimeSession:
    _ = request.state.user_id
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    session = await runtime_gateway.bootstrap(build)
    await build_store.append_event(
        build_id,
        event_type="RUNTIME_BOOTSTRAPPED",
        payload={
            "runtime_id": str(session.runtime_id),
            "status": session.status,
        },
    )
    return session


@router.get("/v1/builds/{build_id}/runtime/status", response_model=RuntimeSession)
async def runtime_status(build_id: UUID) -> RuntimeSession:
    session = await runtime_gateway.get_session(build_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "runtime_not_found", "message": "Runtime session not found."},
        )
    return session


@router.post("/v1/builds/{build_id}/runtime/tick", response_model=RuntimeTickResult)
@limiter.limit(rate_limit_string())
async def runtime_tick(build_id: UUID, request: Request) -> RuntimeTickResult:
    _ = request.state.user_id
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )

    try:
        result = await runtime_gateway.tick(build)
        for node_id in result.executed_nodes:
            task_run = await build_store.start_task_run(
                build_id,
                node_id=node_id,
                source="runtime_tick",
            )
            await build_store.finish_task_run(
                build_id,
                task_run_id=task_run.task_run_id,
                status=TaskStatus.completed,
                source="runtime_tick",
            )

            node = next((item for item in build.dag if item.node_id == node_id), None)
            if node is not None and node.gate is not None:
                await build_store.record_gate_decision(
                    build_id,
                    gate=node.gate,
                    status=GateDecisionStatus.pass_,
                    reason="runtime_auto_pass",
                    node_id=node_id,
                    source="runtime_tick",
                )

        if result.finished and build.status != BuildStatus.completed:
            await build_store.complete_build(build_id, reason="runtime_tick_completed")
        return result
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "runtime_tick_conflict", "message": str(exc)},
        ) from exc
