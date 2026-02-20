"""Vibe-to-Production API — FastAPI application entry point.

Start with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.middleware.auth import SupabaseAuthMiddleware
from api.middleware.rate_limit import limiter
from api.routes import (
    audit,
    status,
    fix,
    primer,
    onboarding,
    github_oauth,
    webhook,
    vision_intake,
    builds,
    runtime,
)
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Clarity Check API starting up...")
    if settings.tier1_enabled:
        await audit.cleanup_tier1_expired()
    yield
    logger.info("Clarity Check API shutting down.")


app = FastAPI(
    title="Clarity Check API",
    description=(
        "AI-powered code audit API. Hermes orchestrates specialist agents "
        "(Primer → Scanner → Evolution → Builder → Security → Planner → Educator) "
        "to analyze a GitHub repository and produce a prioritised remediation "
        "report with real-time SSE streaming."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------ #
# CORS
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    # Dev-friendly: allow any localhost port (Vite will hop ports if one is taken).
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
# Rate limiting
# ------------------------------------------------------------------ #
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ------------------------------------------------------------------ #
# JWT Auth (skip for health + docs)
# ------------------------------------------------------------------ #
app.add_middleware(SupabaseAuthMiddleware)

# ------------------------------------------------------------------ #
# Routers
# ------------------------------------------------------------------ #
app.include_router(audit.router, prefix="/api", tags=["audit"])
app.include_router(status.router, prefix="/api", tags=["streaming"])
app.include_router(fix.router, prefix="/api", tags=["fix"])
app.include_router(primer.router, prefix="/api", tags=["primer"])
app.include_router(onboarding.router, prefix="/api", tags=["onboarding"])
app.include_router(github_oauth.router, prefix="/api", tags=["github"])
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
app.include_router(vision_intake.router, prefix="/api", tags=["vision-intake"])
app.include_router(builds.router, tags=["builds"])
app.include_router(runtime.router, tags=["runtime"])


# ------------------------------------------------------------------ #
# Health & root
# ------------------------------------------------------------------ #
@app.get("/", tags=["meta"])
async def root():
    return {"service": "Clarity Check API", "status": "ok", "version": "1.0.0"}


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "healthy"}


# ------------------------------------------------------------------ #
# Global error handler
# ------------------------------------------------------------------ #
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
