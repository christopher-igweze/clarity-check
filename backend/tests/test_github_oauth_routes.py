"""Route-level tests for GitHub OAuth lifecycle."""

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
os.environ.setdefault("GITHUB_CLIENT_ID", "test-client")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test-secret")

from api.routes import github_oauth  # noqa: E402


class GithubOAuthRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = github_oauth.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(github_oauth.router, prefix="/api")
        cls.client = TestClient(app)

    def test_get_auth_url_returns_stateful_redirect(self) -> None:
        with patch.object(github_oauth.settings, "github_client_id", "test-client"), patch.object(
            github_oauth.settings, "github_client_secret", "test-secret"
        ):
            resp = self.client.post(
                "/api/github-oauth",
                json={
                    "action": "get_auth_url",
                    "redirect_uri": "http://localhost:5173/settings",
                },
            )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload["auth_url"].startswith("https://github.com/login/oauth/authorize?"))
        self.assertIn("state=", payload["auth_url"])

    def test_exchange_code_persists_connection(self) -> None:
        with patch.object(github_oauth.settings, "github_client_id", "test-client"), patch.object(
            github_oauth.settings, "github_client_secret", "test-secret"
        ):
            auth_resp = self.client.post(
                "/api/github-oauth",
                json={
                    "action": "get_auth_url",
                    "redirect_uri": "http://localhost:5173/settings",
                },
            )
        self.assertEqual(auth_resp.status_code, 200)
        state = auth_resp.json()["auth_url"].split("state=", 1)[1]

        with patch.object(github_oauth.settings, "github_client_id", "test-client"), patch.object(
            github_oauth.settings, "github_client_secret", "test-secret"
        ), patch(
            "api.routes.github_oauth._exchange_code_for_access_token",
            new=AsyncMock(return_value="gho_test_token"),
        ), patch(
            "api.routes.github_oauth._fetch_github_profile",
            new=AsyncMock(return_value=("octocat", "https://avatars.githubusercontent.com/u/1")),
        ), patch(
            "api.routes.github_oauth.db.save_github_connection",
            new=AsyncMock(),
        ) as mock_save:
            resp = self.client.post(
                "/api/github-oauth",
                json={
                    "action": "exchange_code",
                    "code": "abc123",
                    "redirect_uri": "http://localhost:5173/settings",
                    "state": state,
                },
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload["connected"])
        self.assertEqual(payload["github_username"], "octocat")
        mock_save.assert_awaited_once()

    def test_disconnect_clears_connection(self) -> None:
        with patch(
            "api.routes.github_oauth.db.clear_github_connection",
            new=AsyncMock(),
        ) as mock_clear:
            resp = self.client.post("/api/github-oauth", json={"action": "disconnect"})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["connected"], False)
        mock_clear.assert_awaited_once_with(user_id="user_test")


if __name__ == "__main__":
    unittest.main()
