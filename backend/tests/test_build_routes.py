"""Route-level tests for Week 1 /v1/builds orchestration scaffolding."""

from __future__ import annotations

import os
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.routes import builds  # noqa: E402


class BuildRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = builds.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(builds.router)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        builds.limiter.reset()

    @staticmethod
    def _create_payload() -> dict:
        return {
            "repo_url": "https://github.com/octocat/Hello-World",
            "objective": "Week 1 orchestration kickoff",
        }

    def test_create_and_get_build(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        self.assertEqual(create_resp.status_code, 200)

        build = create_resp.json()
        self.assertIn("build_id", build)
        self.assertEqual(build["status"], "running")
        self.assertGreaterEqual(len(build["dag"]), 1)

        build_id = build["build_id"]
        get_resp = self.client.get(f"/v1/builds/{build_id}")
        self.assertEqual(get_resp.status_code, 200)
        fetched = get_resp.json()
        self.assertEqual(fetched["build_id"], build_id)
        self.assertEqual(fetched["repo_url"], self._create_payload()["repo_url"])

    def test_list_builds_filters_by_status(self) -> None:
        created_ids: list[str] = []
        for idx in range(3):
            payload = {
                "repo_url": f"https://github.com/octocat/repo-{idx}",
                "objective": f"objective-{idx}",
            }
            resp = self.client.post("/v1/builds", json=payload)
            self.assertEqual(resp.status_code, 200)
            created_ids.append(resp.json()["build_id"])

        abort_resp = self.client.post(
            f"/v1/builds/{created_ids[0]}/abort",
            json={"reason": "status filter test"},
        )
        self.assertEqual(abort_resp.status_code, 200)

        running_resp = self.client.get("/v1/builds?status=running&limit=20")
        self.assertEqual(running_resp.status_code, 200)
        running_rows = running_resp.json()
        self.assertGreaterEqual(len(running_rows), 2)
        self.assertTrue(all(row["status"] == "running" for row in running_rows))

        aborted_resp = self.client.get("/v1/builds?status=aborted&limit=20")
        self.assertEqual(aborted_resp.status_code, 200)
        aborted_rows = aborted_resp.json()
        self.assertGreaterEqual(len(aborted_rows), 1)
        self.assertTrue(all(row["status"] == "aborted" for row in aborted_rows))

    def test_abort_then_resume_conflict(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        build_id = create_resp.json()["build_id"]

        abort_resp = self.client.post(
            f"/v1/builds/{build_id}/abort",
            json={"reason": "manual test abort"},
        )
        self.assertEqual(abort_resp.status_code, 200)
        self.assertEqual(abort_resp.json()["status"], "aborted")

        resume_resp = self.client.post(
            f"/v1/builds/{build_id}/resume",
            json={"reason": "manual test resume"},
        )
        self.assertEqual(resume_resp.status_code, 409)
        self.assertEqual(resume_resp.json()["detail"]["code"], "build_resume_conflict")

    def test_manual_checkpoint_creation(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        self.assertEqual(create_resp.status_code, 200)
        build_id = create_resp.json()["build_id"]

        checkpoint_resp = self.client.post(
            f"/v1/builds/{build_id}/checkpoints",
            json={"reason": "test_checkpoint"},
        )
        self.assertEqual(checkpoint_resp.status_code, 200)
        checkpoint = checkpoint_resp.json()
        self.assertEqual(checkpoint["build_id"], build_id)
        self.assertEqual(checkpoint["reason"], "test_checkpoint")

        list_resp = self.client.get(f"/v1/builds/{build_id}/checkpoints")
        self.assertEqual(list_resp.status_code, 200)
        checkpoints = list_resp.json()
        self.assertGreaterEqual(len(checkpoints), 2)  # includes initial build_created checkpoint
        self.assertEqual(checkpoints[-1]["reason"], "test_checkpoint")

    def test_manual_gate_decision_pauses_running_build(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        self.assertEqual(create_resp.status_code, 200)
        build_id = create_resp.json()["build_id"]

        gate_resp = self.client.post(
            f"/v1/builds/{build_id}/gates/TEST_GATE",
            json={"status": "BLOCKED", "reason": "needs_human_review"},
        )
        self.assertEqual(gate_resp.status_code, 200)
        decision = gate_resp.json()
        self.assertEqual(decision["gate"], "TEST_GATE")
        self.assertEqual(decision["status"], "BLOCKED")
        self.assertEqual(decision["reason"], "needs_human_review")

        build_resp = self.client.get(f"/v1/builds/{build_id}")
        self.assertEqual(build_resp.status_code, 200)
        self.assertEqual(build_resp.json()["status"], "paused")

        list_gates_resp = self.client.get(f"/v1/builds/{build_id}/gates")
        self.assertEqual(list_gates_resp.status_code, 200)
        gates = list_gates_resp.json()
        self.assertGreaterEqual(len(gates), 1)
        self.assertEqual(gates[0]["status"], "BLOCKED")

    def test_events_stream_contains_core_lifecycle_events(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        build_id = create_resp.json()["build_id"]
        self.client.post(f"/v1/builds/{build_id}/abort", json={"reason": "close stream"})

        events_resp = self.client.get(f"/v1/builds/{build_id}/events")
        self.assertEqual(events_resp.status_code, 200)
        self.assertTrue(events_resp.headers["content-type"].startswith("text/event-stream"))
        self.assertIn("event: BUILD_STARTED", events_resp.text)
        self.assertIn("event: BUILD_ABORTED", events_resp.text)
        self.assertIn("event: BUILD_FINISHED", events_resp.text)
        self.assertIn("event: CHECKPOINT_CREATED", events_resp.text)

    def test_task_run_lifecycle_and_retrieval(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        self.assertEqual(create_resp.status_code, 200)
        build_id = create_resp.json()["build_id"]
        node_id = create_resp.json()["dag"][0]["node_id"]

        start_resp = self.client.post(
            f"/v1/builds/{build_id}/tasks",
            json={"node_id": node_id},
        )
        self.assertEqual(start_resp.status_code, 200)
        task_run = start_resp.json()
        self.assertEqual(task_run["node_id"], node_id)
        self.assertEqual(task_run["status"], "running")

        complete_resp = self.client.post(
            f"/v1/builds/{build_id}/tasks/{task_run['task_run_id']}/complete",
            json={"status": "completed"},
        )
        self.assertEqual(complete_resp.status_code, 200)
        self.assertEqual(complete_resp.json()["status"], "completed")

        list_resp = self.client.get(f"/v1/builds/{build_id}/tasks")
        self.assertEqual(list_resp.status_code, 200)
        rows = list_resp.json()
        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(rows[0]["task_run_id"], task_run["task_run_id"])

        get_resp = self.client.get(
            f"/v1/builds/{build_id}/tasks/{task_run['task_run_id']}"
        )
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["status"], "completed")

        running_filter_resp = self.client.get(
            f"/v1/builds/{build_id}/tasks?status=running"
        )
        self.assertEqual(running_filter_resp.status_code, 200)
        self.assertEqual(len(running_filter_resp.json()), 0)

    def test_list_builds_includes_task_counts(self) -> None:
        create_resp = self.client.post("/v1/builds", json=self._create_payload())
        build_id = create_resp.json()["build_id"]
        node_id = create_resp.json()["dag"][0]["node_id"]

        start_resp = self.client.post(
            f"/v1/builds/{build_id}/tasks",
            json={"node_id": node_id},
        )
        task_run_id = start_resp.json()["task_run_id"]
        self.client.post(
            f"/v1/builds/{build_id}/tasks/{task_run_id}/complete",
            json={"status": "failed", "error": "unit_test_failure"},
        )

        list_resp = self.client.get("/v1/builds?limit=10")
        self.assertEqual(list_resp.status_code, 200)
        rows = list_resp.json()
        target = next((row for row in rows if row["build_id"] == build_id), None)
        self.assertIsNotNone(target)
        self.assertEqual(target["task_total"], 1)
        self.assertEqual(target["task_completed"], 0)
        self.assertEqual(target["task_failed"], 1)


if __name__ == "__main__":
    unittest.main()
