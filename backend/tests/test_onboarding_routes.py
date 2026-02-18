"""Route-level tests for onboarding payload validation and persistence calls."""

from __future__ import annotations

import os
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.routes.onboarding import router  # noqa: E402


class OnboardingRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(router, prefix="/api")
        cls.client = TestClient(app)

    @staticmethod
    def _base_payload() -> dict:
        return {
            "technical_level": "founder",
            "explanation_style": "teach_me",
            "shipping_posture": "balanced",
            "tool_tags": ["React"],
            "acquisition_source": "google_search",
            "acquisition_other": None,
            "coding_agent_provider": "openai",
            "coding_agent_model": "openai/gpt-5.2-codex",
        }

    def test_missing_required_coding_agent_fields_returns_422(self) -> None:
        payload = self._base_payload()
        payload.pop("coding_agent_provider")

        resp = self.client.post("/api/onboarding/org", json=payload)

        self.assertEqual(resp.status_code, 422)

    def test_save_onboarding_persists_payload(self) -> None:
        payload = self._base_payload()
        mock_save = AsyncMock()

        with patch("api.routes.onboarding.db.save_org_onboarding", new=mock_save):
            resp = self.client.post("/api/onboarding/org", json=payload)

        self.assertEqual(resp.status_code, 200)
        mock_save.assert_awaited_once_with(user_id="user_test", payload=payload)


if __name__ == "__main__":
    unittest.main()
