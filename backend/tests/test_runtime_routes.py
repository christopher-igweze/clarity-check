"""Route-level tests for runtime bootstrap/tick scaffolding."""

from __future__ import annotations

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
from orchestration.store import build_store  # noqa: E402


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

    def _create_build(self, dag: list[dict] | None = None) -> str:
        payload = {
            "repo_url": "https://github.com/octocat/Hello-World",
            "objective": "runtime test build",
        }
        if dag is not None:
            payload["dag"] = dag
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


if __name__ == "__main__":
    unittest.main()
