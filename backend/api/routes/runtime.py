"""Runtime routes for Week 1 runner gateway scaffolding."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from api.middleware.rate_limit import limiter, rate_limit_string
from models.builds import BuildStatus, GateDecisionStatus, GateType, ReplanAction, TaskStatus
from models.runtime import (
    RuntimeMetric,
    RuntimeRunLog,
    RuntimeSession,
    RuntimeTelemetrySummary,
    RuntimeTickResult,
)
from orchestration.runner_bridge import runner_bridge
from orchestration.runtime_gateway import runtime_gateway
from orchestration.store import build_store
from orchestration.telemetry import list_runtime_metrics, summarize_runtime_metrics

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


@router.get("/v1/builds/{build_id}/runtime/metrics", response_model=list[RuntimeMetric])
async def runtime_metrics(
    build_id: UUID,
    metric: str | None = None,
    limit: int = 200,
) -> list[RuntimeMetric]:
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    return await list_runtime_metrics(
        build_id=build_id,
        metric=metric,
        limit=limit,
    )


@router.get("/v1/builds/{build_id}/runtime/telemetry", response_model=RuntimeTelemetrySummary)
async def runtime_telemetry(build_id: UUID) -> RuntimeTelemetrySummary:
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    return await summarize_runtime_metrics(build_id)


@router.get("/v1/builds/{build_id}/runtime/logs", response_model=list[RuntimeRunLog])
async def runtime_logs(
    build_id: UUID,
    node_id: str | None = None,
    status: str | None = None,
    limit: int = 200,
) -> list[RuntimeRunLog]:
    build = await build_store.get_build(build_id)
    if build is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        )
    return await runner_bridge.list_logs(
        build_id=build_id,
        node_id=node_id,
        status=status,
        limit=limit,
    )


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
        if result.level_started is not None:
            levels = build.metadata.get("dag_levels", [])
            next_nodes = []
            if isinstance(levels, list) and result.level_started < len(levels):
                nodes_at_level = levels[result.level_started]
                if isinstance(nodes_at_level, list):
                    next_nodes = [str(node_id) for node_id in nodes_at_level]
            await build_store.append_event(
                build_id,
                event_type="LEVEL_STARTED",
                payload={"level": result.level_started, "nodes": next_nodes},
            )

        for node_id in result.executed_nodes:
            task_run = await build_store.start_task_run(
                build_id,
                node_id=node_id,
                source="runtime_tick",
            )
            run_log = await runner_bridge.execute(
                build=build,
                runtime_id=result.runtime_id,
                node_id=node_id,
            )
            await build_store.append_event(
                build_id,
                event_type="RUNNER_RESULT",
                payload={
                    "log_id": str(run_log.log_id),
                    "node_id": run_log.node_id,
                    "runner": run_log.runner,
                    "workspace_id": run_log.workspace_id,
                    "status": run_log.status,
                    "duration_ms": run_log.duration_ms,
                    "error": run_log.error,
                },
            )

            if run_log.status == "failed":
                await build_store.finish_task_run(
                    build_id,
                    task_run_id=task_run.task_run_id,
                    status=TaskStatus.failed,
                    error=run_log.error or run_log.message,
                    source="runtime_tick",
                )
                retry_budget = max(0, int(build.metadata.get("max_task_retries", 0)))
                should_retry = task_run.attempt <= retry_budget

                if should_retry:
                    retry_level = await runtime_gateway.mark_node_for_retry(
                        build,
                        node_id=node_id,
                    )
                    await build_store.record_replan_decision(
                        build_id,
                        action=ReplanAction.continue_,
                        reason=f"retry_node:{node_id}:attempt_{task_run.attempt}",
                        replacement_nodes=[],
                        source="runtime_tick",
                    )
                    await build_store.append_event(
                        build_id,
                        event_type="TASK_RETRY_SCHEDULED",
                        payload={
                            "node_id": node_id,
                            "attempt": task_run.attempt,
                            "next_attempt": task_run.attempt + 1,
                            "retry_budget": retry_budget,
                            "retry_level": retry_level,
                        },
                    )
                    result.finished = False
                    if node_id not in result.pending_nodes:
                        result.pending_nodes.append(node_id)
                        result.pending_nodes.sort()
                    continue

                await build_store.record_gate_decision(
                    build_id,
                    gate=GateType.policy,
                    status=GateDecisionStatus.fail,
                    reason="runner_execution_failed",
                    node_id=node_id,
                    source="runtime_tick",
                )
                if build.status != BuildStatus.failed:
                    await build_store.fail_build(
                        build_id,
                        reason=f"runner_failed:{node_id}",
                    )
                continue

            task_status = TaskStatus.skipped if run_log.status == "skipped" else TaskStatus.completed
            await build_store.finish_task_run(
                build_id,
                task_run_id=task_run.task_run_id,
                status=task_status,
                source="runtime_tick",
            )

            node = next((item for item in build.dag if item.node_id == node_id), None)
            if node is not None and node.gate is not None and task_status == TaskStatus.completed:
                await build_store.record_gate_decision(
                    build_id,
                    gate=node.gate,
                    status=GateDecisionStatus.pass_,
                    reason="runtime_auto_pass",
                    node_id=node_id,
                    source="runtime_tick",
                )

        if result.finished and build.status == BuildStatus.running:
            await build_store.complete_build(build_id, reason="runtime_tick_completed")
        return result
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "runtime_tick_conflict", "message": str(exc)},
        ) from exc
