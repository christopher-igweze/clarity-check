"""Unit tests for adaptive autonomous DAG planner profile."""

from __future__ import annotations

import unittest

from orchestration.dag_planner import plan_adaptive_autonomous_dag, plan_agentic_llm_dag


class AdaptiveDagPlannerTests(unittest.TestCase):
    def test_adaptive_plan_adds_parallel_branches_and_flow_guards(self) -> None:
        dag, trace = plan_adaptive_autonomous_dag(
            {
                "project_intake": {
                    "must_not_break_flows": ["Checkout flow", "Account login"],
                    "sensitive_data": ["none"],
                    "scale_expectation": "medium",
                }
            }
        )
        node_ids = [node.node_id for node in dag]
        self.assertIn("scanner", node_ids)
        self.assertIn("dependency-audit", node_ids)
        self.assertIn("architecture-review", node_ids)
        self.assertIn("test-baseline", node_ids)
        self.assertIn("dynamic-probe", node_ids)
        self.assertIn("security-review", node_ids)
        self.assertIn("flow-guard-checkout-flow", node_ids)
        self.assertIn("flow-guard-account-login", node_ids)
        self.assertIn("planner", node_ids)
        self.assertEqual(trace["profile"], "adaptive_parallel_v1")
        self.assertEqual(trace["flow_guards"], 2)
        self.assertFalse(trace["sensitive_data_review"])
        self.assertFalse(trace["scale_readiness_check"])

    def test_adaptive_plan_adds_sensitive_and_scale_nodes(self) -> None:
        dag, trace = plan_adaptive_autonomous_dag(
            {
                "project_intake": {
                    "must_not_break_flows": [],
                    "sensitive_data": ["pii"],
                    "scale_expectation": "high",
                }
            }
        )
        node_ids = [node.node_id for node in dag]
        self.assertIn("data-boundary-review", node_ids)
        self.assertIn("scale-readiness-check", node_ids)
        self.assertTrue(trace["sensitive_data_review"])
        self.assertTrue(trace["scale_readiness_check"])

    def test_agentic_profile_uses_blueprint_when_provided(self) -> None:
        dag, trace = plan_agentic_llm_dag(
            metadata={
                "planner_dag_blueprint": [
                    {
                        "node_id": "scan",
                        "title": "Scan",
                        "agent": "scanner",
                        "depends_on": [],
                    },
                    {
                        "node_id": "plan",
                        "title": "Plan",
                        "agent": "planner",
                        "depends_on": ["scan"],
                        "gate": "MERGE_GATE",
                    },
                ]
            },
            objective="test objective",
        )
        self.assertEqual([node.node_id for node in dag], ["scan", "plan"])
        self.assertEqual(trace["profile"], "agentic_llm_v1")
        self.assertEqual(trace["source"], "planner_dag_blueprint")

    def test_agentic_profile_falls_back_when_blueprint_is_invalid(self) -> None:
        dag, trace = plan_agentic_llm_dag(
            metadata={
                "planner_dag_blueprint": [
                    {"node_id": "dup", "title": "A", "agent": "scanner"},
                    {"node_id": "dup", "title": "B", "agent": "planner"},
                ]
            },
            objective="test objective",
        )
        node_ids = [node.node_id for node in dag]
        self.assertIn("scanner", node_ids)
        self.assertEqual(trace["profile"], "agentic_llm_v1_fallback")


if __name__ == "__main__":
    unittest.main()
