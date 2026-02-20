"""DAG scheduler helpers for orchestration runtime level execution."""

from __future__ import annotations

from collections import defaultdict

from models.builds import DagNode


def compute_dag_levels(dag: list[DagNode]) -> list[list[str]]:
    """Return deterministic execution levels for an acyclic DAG.

    Raises ValueError with a machine-readable message when the DAG is invalid.
    """
    if not dag:
        return []

    by_id: dict[str, DagNode] = {}
    for node in dag:
        if node.node_id in by_id:
            raise ValueError(f"duplicate_node_id:{node.node_id}")
        by_id[node.node_id] = node

    indegree: dict[str, int] = {}
    dependents: dict[str, list[str]] = defaultdict(list)
    for node in dag:
        deps = list(node.depends_on)
        if node.node_id in deps:
            raise ValueError(f"self_dependency:{node.node_id}")
        for dep in deps:
            if dep not in by_id:
                raise ValueError(f"missing_dependency:{dep}")
            dependents[dep].append(node.node_id)
        indegree[node.node_id] = len(deps)

    ready = sorted([node_id for node_id, degree in indegree.items() if degree == 0])
    levels: list[list[str]] = []
    visited = 0
    while ready:
        level = list(ready)
        levels.append(level)
        visited += len(level)
        next_ready: list[str] = []
        for node_id in level:
            for child in sorted(dependents.get(node_id, [])):
                indegree[child] -= 1
                if indegree[child] == 0:
                    next_ready.append(child)
        ready = sorted(next_ready)

    if visited != len(dag):
        raise ValueError("dag_cycle_detected")
    return levels


def find_level(levels: list[list[str]], *, node_id: str) -> int | None:
    for idx, level in enumerate(levels):
        if node_id in level:
            return idx
    return None

