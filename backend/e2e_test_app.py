"""Shared app/client helpers for backend e2e route tests."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.middleware.rate_limit import limiter  # noqa: E402
from api.routes import builds, program, runtime, validation  # noqa: E402


def create_e2e_client() -> TestClient:
    app = FastAPI()
    app.state.limiter = limiter

    @app.middleware("http")
    async def _inject_user(request, call_next):
        request.state.user_id = request.headers.get("X-Test-User", "e2e_default_user")
        return await call_next(request)

    app.include_router(builds.router)
    app.include_router(runtime.router)
    app.include_router(validation.router)
    app.include_router(program.router)
    return TestClient(app)


def reset_rate_limiter() -> None:
    limiter.reset()

