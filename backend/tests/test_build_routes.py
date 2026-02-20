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


if __name__ == "__main__":
    unittest.main()

