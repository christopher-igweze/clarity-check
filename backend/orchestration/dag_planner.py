"""Adaptive DAG planner primitives for autonomous control-plane builds."""

from __future__ import annotations

import json
import re
from typing import Any

from models.builds import DagNode, GateType


def _slug(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned[:40]


def _normalize_flows(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    rows = [str(item).strip() for item in raw if str(item).strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for row in rows:
        key = row.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _has_sensitive_data(raw: object) -> bool:
    if not isinstance(raw, list):
        return False
    normalized = {str(item).strip().lower() for item in raw}
    normalized.discard("")
    normalized.discard("none")
    normalized.discard("not_sure")
    return bool(normalized)


def plan_adaptive_autonomous_dag(metadata: dict[str, Any]) -> tuple[list[DagNode], dict[str, Any]]:
    """Build an adaptive multi-branch DAG from intake metadata.

    This is a deterministic planner profile intended to increase default
    parallelism while keeping explicit gates and fail-closed semantics.
    """
    intake = metadata.get("project_intake")
    intake_payload = intake if isinstance(intake, dict) else {}
    flows = _normalize_flows(intake_payload.get("must_not_break_flows"))
    has_sensitive_data = _has_sensitive_data(intake_payload.get("sensitive_data"))
    scale_expectation = str(intake_payload.get("scale_expectation") or "").strip().lower()
    high_scale = scale_expectation in {"high", "very_high", "very high", "large"}

    dag: list[DagNode] = [
        DagNode(
            node_id="scanner",
            title="Static scan",
            agent="scanner",
            depends_on=[],
        ),
        DagNode(
            node_id="dependency-audit",
            title="Dependency + supply-chain audit",
            agent="security",
            depends_on=["scanner"],
        ),
        DagNode(
            node_id="architecture-review",
            title="Architecture and boundary review",
            agent="planner",
            depends_on=["scanner"],
        ),
        DagNode(
            node_id="test-baseline",
            title="Baseline test and build verification",
            agent="builder",
            depends_on=["scanner"],
            gate=GateType.test,
        ),
        DagNode(
            node_id="dynamic-probe",
            title="Dynamic probe and runtime checks",
            agent="builder",
            depends_on=["test-baseline", "dependency-audit"],
            gate=GateType.test,
        ),
        DagNode(
            node_id="security-review",
            title="Security review",
            agent="security",
            depends_on=["dependency-audit", "architecture-review"],
            gate=GateType.policy,
        ),
    ]

    flow_guard_nodes: list[str] = []
    for idx, flow in enumerate(flows[:4]):
        node_slug = _slug(flow) or f"flow-{idx + 1}"
        node_id = f"flow-guard-{node_slug}"
        dag.append(
            DagNode(
                node_id=node_id,
                title=f"Flow guard: {flow}",
                agent="builder",
                depends_on=["test-baseline"],
                gate=GateType.test,
            )
        )
        flow_guard_nodes.append(node_id)

    security_terminal = "security-review"
    if has_sensitive_data:
        security_terminal = "data-boundary-review"
        dag.append(
            DagNode(
                node_id=security_terminal,
                title="Data boundary + secret handling review",
                agent="security",
                depends_on=["security-review"],
                gate=GateType.policy,
            )
        )

    performance_node = None
    if high_scale:
        performance_node = "scale-readiness-check"
        dag.append(
            DagNode(
                node_id=performance_node,
                title="Scale readiness check",
                agent="builder",
                depends_on=["dynamic-probe"],
                gate=GateType.test,
            )
        )

    planner_dependencies = ["dynamic-probe", "architecture-review", security_terminal, *flow_guard_nodes]
    if performance_node:
        planner_dependencies.append(performance_node)
    dag.append(
        DagNode(
            node_id="planner",
            title="Remediation plan",
            agent="planner",
            depends_on=sorted(set(planner_dependencies)),
            gate=GateType.merge,
        )
    )

    planner_trace = {
        "profile": "adaptive_parallel_v1",
        "flow_guards": len(flow_guard_nodes),
        "sensitive_data_review": has_sensitive_data,
        "scale_readiness_check": bool(performance_node),
    }
    return dag, planner_trace


def plan_agentic_llm_dag(
    *,
    metadata: dict[str, Any],
    objective: str,
) -> tuple[list[DagNode], dict[str, Any]]:
    """Build DAG using agentic profile inputs with safe deterministic fallback.

    This profile accepts a pre-generated planner blueprint (`planner_dag_blueprint`)
    to support future planner-agent synthesis while maintaining strict validation
    and deterministic fallback behavior.
    """
    blueprint = _parse_blueprint(metadata.get("planner_dag_blueprint"))
    if blueprint:
        return (
            blueprint,
            {
                "profile": "agentic_llm_v1",
                "source": "planner_dag_blueprint",
                "objective": objective[:180],
                "node_count": len(blueprint),
            },
        )

    fallback_dag, fallback_trace = plan_adaptive_autonomous_dag(metadata)
    return (
        fallback_dag,
        {
            **fallback_trace,
            "profile": "agentic_llm_v1_fallback",
            "source": "adaptive_parallel_v1",
            "objective": objective[:180],
        },
    )


def _parse_blueprint(raw: object) -> list[DagNode]:
    payload = raw
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            return []
    if not isinstance(payload, list):
        return []

    nodes: list[DagNode] = []
    seen: set[str] = set()
    for entry in payload:
        if not isinstance(entry, dict):
            return []
        node_id = str(entry.get("node_id") or "").strip()
        title = str(entry.get("title") or "").strip()
        agent = str(entry.get("agent") or "").strip().lower()
        if not node_id or not title or not agent:
            return []
        if node_id in seen:
            return []
        seen.add(node_id)

        depends_on_raw = entry.get("depends_on", [])
        if isinstance(depends_on_raw, list):
            depends_on = [str(item).strip() for item in depends_on_raw if str(item).strip()]
        else:
            depends_on = []

        gate_raw = entry.get("gate")
        gate: GateType | None = None
        if isinstance(gate_raw, str) and gate_raw.strip():
            normalized_gate = gate_raw.strip().upper()
            if normalized_gate not in {member.value for member in GateType}:
                return []
            gate = GateType(normalized_gate)

        nodes.append(
            DagNode(
                node_id=node_id,
                title=title,
                agent=agent,
                depends_on=depends_on,
                gate=gate,
            )
        )
    return nodes
