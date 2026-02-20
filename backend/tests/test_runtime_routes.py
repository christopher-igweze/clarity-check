"""Route-level tests for runtime bootstrap/tick scaffolding."""

from __future__ import annotations

import asyncio
import os
import unittest
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.routes import builds, runtime  # noqa: E402
from orchestration.runner_bridge import runner_bridge  # noqa: E402
from orchestration.store import build_store  # noqa: E402
from orchestration.telemetry import reset_runtime_metrics  # noqa: E402


class RuntimeRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = builds.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(builds.router)
        app.include_router(runtime.router)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        builds.limiter.reset()
        asyncio.run(reset_runtime_metrics())
        asyncio.run(runner_bridge.reset())

    def _create_build(
        self,
        dag: list[dict] | None = None,
        metadata: dict | None = None,
    ) -> str:
        payload = {
            "repo_url": "https://github.com/octocat/Hello-World",
            "objective": "runtime test build",
        }
        if dag is not None:
            payload["dag"] = dag
        if metadata is not None:
            payload["metadata"] = metadata
        resp = self.client.post(
            "/v1/builds",
            json=payload,
        )
        self.assertEqual(resp.status_code, 200)
        return resp.json()["build_id"]

    def test_runtime_bootstrap_and_status(self) -> None:
        build_id = self._create_build()
        boot_resp = self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")
        self.assertEqual(boot_resp.status_code, 200)
        session = boot_resp.json()
        self.assertEqual(session["build_id"], build_id)

        status_resp = self.client.get(f"/v1/builds/{build_id}/runtime/status")
        self.assertEqual(status_resp.status_code, 200)
        self.assertEqual(status_resp.json()["runtime_id"], session["runtime_id"])

    def test_runtime_tick_emits_completion(self) -> None:
        build_id = self._create_build()
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")

        max_ticks = 10
        finished = False
        for _ in range(max_ticks):
            tick_resp = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
            self.assertEqual(tick_resp.status_code, 200)
            payload = tick_resp.json()
            finished = bool(payload.get("finished"))
            if finished:
                break

        self.assertTrue(finished)

        build_resp = self.client.get(f"/v1/builds/{build_id}")
        self.assertEqual(build_resp.status_code, 200)
        build_payload = build_resp.json()
        self.assertEqual(build_payload["status"], "completed")
        self.assertGreaterEqual(len(build_payload["state_transitions"]), 2)

        transitions = [
            (row["from_status"], row["to_status"])
            for row in build_payload["state_transitions"]
        ]
        self.assertIn(("pending", "running"), transitions)
        self.assertIn(("running", "completed"), transitions)

        tasks_resp = self.client.get(f"/v1/builds/{build_id}/tasks")
        self.assertEqual(tasks_resp.status_code, 200)
        tasks = tasks_resp.json()
        self.assertGreaterEqual(len(tasks), 1)
        self.assertTrue(all(task["status"] == "completed" for task in tasks))

        first_task_id = tasks[0]["task_run_id"]
        task_resp = self.client.get(f"/v1/builds/{build_id}/tasks/{first_task_id}")
        self.assertEqual(task_resp.status_code, 200)
        self.assertEqual(task_resp.json()["status"], "completed")

        # Validate event emission from the shared in-memory store by build id.
        events = build_store._events.get(UUID(build_id), [])
        event_types = [entry.event_type for entry in events]
        self.assertIn("TASK_COMPLETED", event_types)
        self.assertIn("BUILD_FINISHED", event_types)

    def test_runtime_tick_records_gate_decision_for_gated_node(self) -> None:
        build_id = self._create_build(
            dag=[
                {"node_id": "scanner", "title": "scan", "agent": "scanner", "depends_on": []},
                {
                    "node_id": "merge_gate",
                    "title": "merge gate",
                    "agent": "planner",
                    "depends_on": ["scanner"],
                    "gate": "MERGE_GATE",
                },
            ]
        )
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")
        for _ in range(5):
            tick_resp = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
            self.assertEqual(tick_resp.status_code, 200)
            if tick_resp.json().get("finished"):
                break

        gates_resp = self.client.get(f"/v1/builds/{build_id}/gates")
        self.assertEqual(gates_resp.status_code, 200)
        gates = gates_resp.json()
        self.assertGreaterEqual(len(gates), 1)
        self.assertEqual(gates[0]["gate"], "MERGE_GATE")
        self.assertEqual(gates[0]["status"], "PASS")

    def test_runtime_metrics_and_summary_endpoints(self) -> None:
        build_id = self._create_build()
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")
        self.client.post(f"/v1/builds/{build_id}/runtime/tick")

        metrics_resp = self.client.get(f"/v1/builds/{build_id}/runtime/metrics")
        self.assertEqual(metrics_resp.status_code, 200)
        metrics = metrics_resp.json()
        self.assertGreaterEqual(len(metrics), 2)
        metric_names = {row["metric"] for row in metrics}
        self.assertIn("runtime_bootstrap", metric_names)
        self.assertIn("runtime_tick", metric_names)

        tick_metrics_resp = self.client.get(
            f"/v1/builds/{build_id}/runtime/metrics?metric=runtime_tick&limit=5"
        )
        self.assertEqual(tick_metrics_resp.status_code, 200)
        tick_metrics = tick_metrics_resp.json()
        self.assertGreaterEqual(len(tick_metrics), 1)
        self.assertTrue(all(row["metric"] == "runtime_tick" for row in tick_metrics))

        summary_resp = self.client.get(f"/v1/builds/{build_id}/runtime/telemetry")
        self.assertEqual(summary_resp.status_code, 200)
        summary = summary_resp.json()
        self.assertEqual(summary["build_id"], build_id)
        self.assertGreaterEqual(summary["metric_count"], 2)
        self.assertGreaterEqual(summary["bootstrap_count"], 1)
        self.assertGreaterEqual(summary["tick_count"], 1)

    def test_runtime_logs_endpoint_returns_normalized_runner_records(self) -> None:
        build_id = self._create_build()
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")
        self.client.post(f"/v1/builds/{build_id}/runtime/tick")

        logs_resp = self.client.get(f"/v1/builds/{build_id}/runtime/logs")
        self.assertEqual(logs_resp.status_code, 200)
        logs = logs_resp.json()
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0]["runner"], "openhands")
        self.assertEqual(logs[0]["status"], "completed")

    def test_runtime_tick_fails_closed_when_runner_returns_failure(self) -> None:
        build_id = self._create_build(
            dag=[
                {"node_id": "scanner", "title": "scan", "agent": "scanner", "depends_on": []},
                {"node_id": "builder", "title": "build", "agent": "builder", "depends_on": ["scanner"]},
            ],
            metadata={
                "runner_results": {
                    "scanner": {
                        "runner": "daytona-openhands",
                        "workspace_id": "ws-daytona-1",
                        "status": "failed",
                        "error": "integration test gate failed",
                    }
                }
            },
        )

        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")
        tick_resp = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(tick_resp.status_code, 200)

        build_resp = self.client.get(f"/v1/builds/{build_id}")
        self.assertEqual(build_resp.status_code, 200)
        build_payload = build_resp.json()
        self.assertEqual(build_payload["status"], "failed")

        task_resp = self.client.get(f"/v1/builds/{build_id}/tasks")
        self.assertEqual(task_resp.status_code, 200)
        tasks = task_resp.json()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["status"], "failed")

        gates_resp = self.client.get(f"/v1/builds/{build_id}/gates")
        self.assertEqual(gates_resp.status_code, 200)
        gate_rows = gates_resp.json()
        self.assertGreaterEqual(len(gate_rows), 1)
        self.assertEqual(gate_rows[0]["gate"], "POLICY_GATE")
        self.assertEqual(gate_rows[0]["status"], "FAIL")

        logs_resp = self.client.get(f"/v1/builds/{build_id}/runtime/logs?status=failed")
        self.assertEqual(logs_resp.status_code, 200)
        logs = logs_resp.json()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["workspace_id"], "ws-daytona-1")
        self.assertEqual(logs[0]["status"], "failed")

    def test_runtime_tick_retries_within_budget_then_completes(self) -> None:
        build_id = self._create_build(
            dag=[
                {"node_id": "scanner", "title": "scan", "agent": "scanner", "depends_on": []},
            ],
            metadata={
                "max_task_retries": 1,
                "runner_results": {
                    "scanner": {
                        "runner": "daytona-openhands",
                        "status_sequence": ["failed", "completed"],
                        "error_sequence": ["transient install timeout", None],
                    }
                },
            },
        )
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")

        tick_one = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(tick_one.status_code, 200)
        self.assertFalse(tick_one.json()["finished"])

        build_mid = self.client.get(f"/v1/builds/{build_id}").json()
        self.assertEqual(build_mid["status"], "running")
        self.assertGreaterEqual(len(build_mid["replan_history"]), 1)
        self.assertEqual(build_mid["replan_history"][0]["action"], "CONTINUE")

        tick_two = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(tick_two.status_code, 200)
        self.assertTrue(tick_two.json()["finished"])

        build_final = self.client.get(f"/v1/builds/{build_id}").json()
        self.assertEqual(build_final["status"], "completed")

        tasks = self.client.get(f"/v1/builds/{build_id}/tasks").json()
        self.assertEqual(len(tasks), 2)
        statuses = {task["status"] for task in tasks}
        self.assertIn("failed", statuses)
        self.assertIn("completed", statuses)

    def test_runtime_tick_fails_after_retry_budget_exhausted(self) -> None:
        build_id = self._create_build(
            dag=[
                {"node_id": "scanner", "title": "scan", "agent": "scanner", "depends_on": []},
            ],
            metadata={
                "max_task_retries": 1,
                "runner_results": {
                    "scanner": {
                        "status_sequence": ["failed", "failed"],
                        "error_sequence": ["attempt 1", "attempt 2"],
                    }
                },
            },
        )
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")

        first_tick = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(first_tick.status_code, 200)
        self.assertFalse(first_tick.json()["finished"])

        second_tick = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(second_tick.status_code, 200)

        build_payload = self.client.get(f"/v1/builds/{build_id}").json()
        self.assertEqual(build_payload["status"], "failed")
        self.assertGreaterEqual(len(build_payload["replan_history"]), 1)

    def test_runtime_tick_executes_single_level_per_tick(self) -> None:
        build_id = self._create_build(
            dag=[
                {"node_id": "a", "title": "A", "agent": "scanner", "depends_on": []},
                {"node_id": "b", "title": "B", "agent": "builder", "depends_on": []},
                {"node_id": "c", "title": "C", "agent": "planner", "depends_on": ["a", "b"]},
            ]
        )
        self.client.post(f"/v1/builds/{build_id}/runtime/bootstrap")

        tick_one = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(tick_one.status_code, 200)
        payload_one = tick_one.json()
        self.assertEqual(set(payload_one["executed_nodes"]), {"a", "b"})
        self.assertFalse(payload_one["finished"])
        self.assertEqual(payload_one["level_started"], 1)

        tick_two = self.client.post(f"/v1/builds/{build_id}/runtime/tick")
        self.assertEqual(tick_two.status_code, 200)
        payload_two = tick_two.json()
        self.assertEqual(payload_two["executed_nodes"], ["c"])
        self.assertTrue(payload_two["finished"])

        events = build_store._events.get(UUID(build_id), [])
        level_events = [entry for entry in events if entry.event_type == "LEVEL_STARTED"]
        self.assertGreaterEqual(len(level_events), 2)
        self.assertEqual(level_events[-1].payload.get("level"), 1)


if __name__ == "__main__":
    unittest.main()
