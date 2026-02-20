"""Route tests for validation planning/reporting endpoints."""

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

from api.routes import validation  # noqa: E402


class ValidationRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = validation.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(validation.router)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        validation.limiter.reset()

    def test_validation_plan_endpoint_builds_run_specs(self) -> None:
        response = self.client.post(
            "/v1/validation/plan",
            json={
                "targets": [
                    {"repo": "https://github.com/org/repo-a", "language": "python", "runs": 2},
                    {"repo": "github.com/org/repo-b", "language": "node", "runs": 1},
                ]
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["target_count"], 2)
        self.assertEqual(body["run_count"], 3)
        self.assertEqual(len(body["runs"]), 3)

    def test_validation_report_endpoint_returns_gate_and_rubric(self) -> None:
        response = self.client.post(
            "/v1/validation/report",
            json={
                "runs": [
                    {
                        "repo": "repo-a",
                        "language": "python",
                        "run_id": "a1",
                        "status": "completed",
                        "duration_ms": 900,
                    },
                    {
                        "repo": "repo-a",
                        "language": "python",
                        "run_id": "a2",
                        "status": "failed",
                        "duration_ms": 3000,
                    },
                    {
                        "repo": "repo-b",
                        "language": "node",
                        "run_id": "b1",
                        "status": "completed",
                        "duration_ms": 1000,
                    },
                ]
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("summary", body)
        self.assertIn("gate", body)
        self.assertIn("rubric", body)
        self.assertFalse(body["rubric"]["release_ready"])
        self.assertGreater(len(body["recommendations"]), 0)


if __name__ == "__main__":
    unittest.main()

