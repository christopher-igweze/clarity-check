"""Week 1 orchestration control-plane routes."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from api.middleware.rate_limit import limiter, rate_limit_string
from models.builds import BuildCreateRequest, BuildRun, BuildStatus
from orchestration.prompt_contracts import list_prompt_contracts
from orchestration.store import build_store

router = APIRouter()


class BuildActionRequest(BaseModel):
    reason: str | None = None


@router.post("/v1/builds", response_model=BuildRun)
@limiter.limit(rate_limit_string())
async def create_build(
    request_body: BuildCreateRequest,
    request: Request,
) -> BuildRun:
    user_id: str = request.state.user_id
    return await build_store.create_build(user_id=user_id, request=request_body)


@router.get("/v1/builds/{build_id}", response_model=BuildRun)
async def get_build(build_id: UUID) -> BuildRun:
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    return build


@router.post("/v1/builds/{build_id}/resume", response_model=BuildRun)
@limiter.limit(rate_limit_string())
async def resume_build(
    build_id: UUID,
    request_body: BuildActionRequest,
    request: Request,
) -> BuildRun:
    _ = request.state.user_id
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
    _ = request.state.user_id
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
async def stream_build_events(build_id: UUID) -> EventSourceResponse:
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    return EventSourceResponse(
        _build_event_generator(build_id),
        media_type="text/event-stream",
    )


@router.get("/v1/prompt-contracts")
async def get_prompt_contracts() -> list[dict]:
    """Expose current prompt contract registry for build/runtime alignment."""
    return [contract.__dict__ for contract in list_prompt_contracts()]

