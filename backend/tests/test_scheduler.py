"""Unit tests for orchestration DAG scheduler."""

from __future__ import annotations

import unittest

from models.builds import DagNode
from orchestration.scheduler import compute_dag_levels, find_level


class SchedulerTests(unittest.TestCase):
    def test_compute_dag_levels_orders_by_dependencies(self) -> None:
        dag = [
            DagNode(node_id="a", title="A", agent="scanner", depends_on=[]),
            DagNode(node_id="b", title="B", agent="builder", depends_on=["a"]),
            DagNode(node_id="c", title="C", agent="planner", depends_on=["a"]),
            DagNode(node_id="d", title="D", agent="security", depends_on=["b", "c"]),
        ]
        levels = compute_dag_levels(dag)
        self.assertEqual(levels, [["a"], ["b", "c"], ["d"]])
        self.assertEqual(find_level(levels, node_id="d"), 2)

    def test_compute_dag_levels_rejects_cycles(self) -> None:
        dag = [
            DagNode(node_id="a", title="A", agent="scanner", depends_on=["b"]),
            DagNode(node_id="b", title="B", agent="builder", depends_on=["a"]),
        ]
        with self.assertRaises(ValueError) as ctx:
            compute_dag_levels(dag)
        self.assertIn("dag_cycle_detected", str(ctx.exception))

    def test_compute_dag_levels_rejects_missing_dependency(self) -> None:
        dag = [
            DagNode(node_id="a", title="A", agent="scanner", depends_on=["missing"]),
        ]
        with self.assertRaises(ValueError) as ctx:
            compute_dag_levels(dag)
        self.assertIn("missing_dependency", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

