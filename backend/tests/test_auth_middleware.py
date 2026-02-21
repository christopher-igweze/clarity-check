"""Behavioral tests for auth middleware response codes and claim handling."""

from __future__ import annotations

import os
import time
import unittest

import jwt
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.middleware.auth import SupabaseAuthMiddleware  # noqa: E402
from config import settings  # noqa: E402


class AuthMiddlewareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.add_middleware(SupabaseAuthMiddleware)

        @app.get("/private")
        async def _private(request: Request):
            return {"user_id": request.state.user_id}

        cls.client = TestClient(app, raise_server_exceptions=False)

    def _token(self, **overrides) -> str:
        now = int(time.time())
        payload = {
            "sub": "auth_middleware_user",
            "aud": "authenticated",
            "iat": now,
            "nbf": now - 5,
            "exp": now + 3600,
            "role": "authenticated",
        }
        payload.update(overrides)
        return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")

    def test_missing_bearer_header_returns_401(self) -> None:
        resp = self.client.get("/private")
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()["detail"], "Missing Bearer token")

    def test_invalid_audience_returns_401_not_500(self) -> None:
        token = self._token(aud="wrong-audience")
        resp = self.client.get("/private", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Invalid token", resp.json()["detail"])

    def test_valid_token_allows_request(self) -> None:
        token = self._token()
        resp = self.client.get("/private", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["user_id"], "auth_middleware_user")


if __name__ == "__main__":
    unittest.main()
