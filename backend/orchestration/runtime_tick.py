"""Shared runtime tick execution logic for API routes and background workers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from config import settings
from models.builds import BuildStatus, GateDecisionStatus, GateType, ReplanAction, TaskRun, TaskStatus
from models.runtime import RuntimeRunLog, RuntimeTickResult
from orchestration.replanner import decide_runtime_replan
from orchestration.runner_bridge import runner_bridge
from orchestration.runtime_gateway import runtime_gateway
from orchestration.store import build_store


@dataclass
class _NodeExecutionResult:
    node_id: str
    task_run: TaskRun
    run_log: RuntimeRunLog


def _extract_policy_violation(run_log: RuntimeRunLog) -> dict[str, Any] | None:
    metadata = run_log.metadata if isinstance(run_log.metadata, dict) else {}
    violation = metadata.get("policy_violation")
    if isinstance(violation, dict):
        return violation
    return None


async def _execute_node(
    *,
    build_id: UUID,
    build,
    runtime_id: UUID,
    node_id: str,
) -> _NodeExecutionResult:
    task_run = await build_store.start_task_run(
        build_id,
        node_id=node_id,
        source="runtime_tick",
    )
    run_log = await runner_bridge.execute(
        build=build,
        runtime_id=runtime_id,
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
    return _NodeExecutionResult(node_id=node_id, task_run=task_run, run_log=run_log)


async def execute_runtime_tick(build_id: UUID) -> RuntimeTickResult:
    build = await build_store.get_build(build_id)
    if build is None:
        raise KeyError("build_not_found")

    result = await runtime_gateway.tick(build)
    if result.level_started is not None:
        levels = build.metadata.get("dag_levels", [])
        next_nodes: list[str] = []
        if isinstance(levels, list) and result.level_started < len(levels):
            nodes_at_level = levels[result.level_started]
            if isinstance(nodes_at_level, list):
                next_nodes = [str(node_id) for node_id in nodes_at_level]
        await build_store.append_event(
            build_id,
            event_type="LEVEL_STARTED",
            payload={"level": result.level_started, "nodes": next_nodes},
        )

    node_parallelism = max(1, int(settings.runtime_node_parallelism))
    runner_kind = str(build.metadata.get("runner_kind") or "").strip().lower()
    if runner_kind in {"openhands_daytona", "daytona-openhands", "daytona_openhands"}:
        # OpenHands tool execution mutates a shared workspace; run sequentially for safety.
        node_parallelism = 1
    semaphore = asyncio.Semaphore(node_parallelism)

    async def _run_with_limit(node_id: str) -> _NodeExecutionResult:
        async with semaphore:
            return await _execute_node(
                build_id=build_id,
                build=build,
                runtime_id=result.runtime_id,
                node_id=node_id,
            )

    executions = await asyncio.gather(*[_run_with_limit(node_id) for node_id in result.executed_nodes])
    for execution in executions:
        node_id = execution.node_id
        task_run = execution.task_run
        run_log = execution.run_log
        policy_violation = _extract_policy_violation(run_log)

        if policy_violation is not None:
            message = str(
                policy_violation.get("message")
                or run_log.error
                or run_log.message
                or "Execution blocked by policy."
            )
            code = str(policy_violation.get("code") or "policy_violation")
            source = str(policy_violation.get("source") or "execution_policy")
            blocking = bool(policy_violation.get("blocking", True))

            await build_store.finish_task_run(
                build_id,
                task_run_id=task_run.task_run_id,
                status=TaskStatus.failed,
                error=message,
                source="runtime_tick",
            )
            await build_store.record_policy_violation(
                build_id,
                code=code,
                message=message,
                source=source,
                blocking=blocking,
            )
            await build_store.record_gate_decision(
                build_id,
                gate=GateType.policy,
                status=GateDecisionStatus.fail,
                reason=f"policy_violation:{code}",
                node_id=node_id,
                source="runtime_tick",
            )
            if blocking and build.status != BuildStatus.failed:
                await build_store.fail_build(
                    build_id,
                    reason=f"policy_violation:{node_id}:{code}",
                )
            continue

        if run_log.status == "failed":
            await build_store.finish_task_run(
                build_id,
                task_run_id=task_run.task_run_id,
                status=TaskStatus.failed,
                error=run_log.error or run_log.message,
                source="runtime_tick",
            )
            retry_budget = max(0, int(build.metadata.get("max_task_retries", 0)))
            replan = decide_runtime_replan(
                build=build,
                node_id=node_id,
                task_run=task_run,
                retry_budget=retry_budget,
            )

            if replan.action == ReplanAction.continue_:
                retry_level = await runtime_gateway.mark_node_for_retry(
                    build,
                    node_id=node_id,
                )
                await build_store.record_replan_decision(
                    build_id,
                    action=ReplanAction.continue_,
                    reason=replan.reason,
                    replacement_nodes=replan.replacement_nodes,
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

            if replan.action == ReplanAction.reduce_scope:
                fallback_applied = await build_store.apply_scan_mode_fallback(
                    build_id,
                    to_mode="deterministic",
                    reason=f"runner_failed:{node_id}",
                    source="runtime_tick",
                )
                if fallback_applied is not None:
                    await runtime_gateway.reset_build_state(
                        fallback_applied,
                        reason=f"fallback_after_failure:{node_id}",
                    )
                    await build_store.record_replan_decision(
                        build_id,
                        action=ReplanAction.reduce_scope,
                        reason=replan.reason,
                        replacement_nodes=replan.replacement_nodes,
                        source="runtime_tick",
                    )
                    result.finished = False
                    result.pending_nodes = sorted([node.node_id for node in fallback_applied.dag])
                    continue

            if replan.action == ReplanAction.abort:
                await build_store.record_replan_decision(
                    build_id,
                    action=ReplanAction.abort,
                    reason=replan.reason,
                    replacement_nodes=replan.replacement_nodes,
                    source="runtime_tick",
                )
                if build.status != BuildStatus.aborted:
                    await build_store.abort_build(
                        build_id,
                        reason=f"replanner_abort:{node_id}",
                    )
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
    final_build = await build_store.get_build(build_id)
    if final_build is not None and final_build.status in {
        BuildStatus.completed,
        BuildStatus.failed,
        BuildStatus.aborted,
    }:
        await runner_bridge.finalize_build(build_id)
    return result
