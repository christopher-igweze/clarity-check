"""Capability authorization tests for program control-plane routes."""

from __future__ import annotations

import os
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.routes import program  # noqa: E402
from config import settings  # noqa: E402


class ProgramCapabilityAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = program.limiter

        @app.middleware("http")
        async def _inject_context(request, call_next):
            request.state.user_id = "capability_user"
            request.state.roles = ["operator"]
            header = request.headers.get("X-Test-Capabilities", "").strip()
            if header:
                request.state.capabilities = [token.strip() for token in header.split(",") if token.strip()]
            else:
                request.state.capabilities = []
            return await call_next(request)

        app.include_router(program.router)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        program.limiter.reset()

    def test_enforced_capability_blocks_secret_write_without_permission(self) -> None:
        original = settings.enforce_capability_auth
        settings.enforce_capability_auth = True
        try:
            resp = self.client.post(
                "/v1/program/secrets",
                json={"name": "token", "value": "plaintext"},
                headers={"X-Test-Capabilities": "program.release.read"},
            )
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(resp.json()["detail"]["code"], "insufficient_capability")
        finally:
            settings.enforce_capability_auth = original

    def test_enforced_capability_allows_secret_write_with_permission(self) -> None:
        original = settings.enforce_capability_auth
        settings.enforce_capability_auth = True
        try:
            resp = self.client.post(
                "/v1/program/secrets",
                json={"name": "token", "value": "plaintext"},
                headers={"X-Test-Capabilities": "program.secrets.write"},
            )
            self.assertEqual(resp.status_code, 200)
        finally:
            settings.enforce_capability_auth = original


if __name__ == "__main__":
    unittest.main()
