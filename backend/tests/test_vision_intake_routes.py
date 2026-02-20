"""Route-level tests for vision intake streaming endpoint."""

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

from api.routes import vision_intake  # noqa: E402


class VisionIntakeRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = vision_intake.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(vision_intake.router, prefix="/api")
        cls.client = TestClient(app)

    def test_stream_returns_sse_with_done(self) -> None:
        resp = self.client.post(
            "/api/vision-intake",
            json={
                "repo_url": "https://github.com/octocat/Hello-World",
                "messages": [
                    {
                        "role": "user",
                        "content": "I'm submitting my repo for audit.",
                    }
                ],
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.headers["content-type"].startswith("text/event-stream"))
        self.assertIn("data: [DONE]", resp.text)
        self.assertIn("single most important user", resp.text)
        self.assertIn("journey that must never", resp.text)


if __name__ == "__main__":
    unittest.main()
