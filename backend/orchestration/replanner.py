"""Bounded replanner decision helpers for runtime failure handling."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.builds import BuildRun, DagNode, ReplanAction, TaskRun


@dataclass
class RuntimeReplanDecision:
    action: ReplanAction | None
    reason: str
    replacement_nodes: list[DagNode] = field(default_factory=list)


def decide_runtime_replan(
    *,
    build: BuildRun,
    node_id: str,
    task_run: TaskRun,
    retry_budget: int,
) -> RuntimeReplanDecision:
    """Return bounded replanner decision for failed task execution.

    Defaults preserve historical behavior:
    - retry when budget allows
    - fallback to deterministic when configured
    - otherwise return `action=None` and let runtime fail gate/build
    """
    if task_run.attempt <= retry_budget:
        return RuntimeReplanDecision(
            action=ReplanAction.continue_,
            reason=f"retry_node:{node_id}:attempt_{task_run.attempt}",
        )

    current_mode = str(build.metadata.get("scan_mode") or "").strip().lower()
    fallback_mode = str(build.metadata.get("fallback_scan_mode") or "").strip().lower()
    fallback_applied = bool(build.metadata.get("fallback_applied"))

    if (
        current_mode == "autonomous"
        and fallback_mode == "deterministic"
        and not fallback_applied
    ):
        return RuntimeReplanDecision(
            action=ReplanAction.reduce_scope,
            reason=f"fallback_to_deterministic:{node_id}",
        )

    if bool(build.metadata.get("replanner_abort_on_terminal_failure")):
        return RuntimeReplanDecision(
            action=ReplanAction.abort,
            reason=f"terminal_failure_abort:{node_id}",
        )

    return RuntimeReplanDecision(
        action=None,
        reason=f"terminal_failure_no_replan:{node_id}",
    )
