"""Supabase JWT verification middleware.

Extracts and validates the Bearer token from the Authorization header
against the Supabase JWT secret.  Attaches ``request.state.user_id``
for downstream route handlers.
"""

from __future__ import annotations

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse

from api.middleware.authorization import derive_roles_and_capabilities
from config import settings

# Paths that don't require authentication
PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
PUBLIC_PREFIXES = ("/api/webhook/",)


class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    def _unauthorized(self, detail: str) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": detail})

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip auth for public endpoints and CORS preflight
        if (
            request.url.path in PUBLIC_PATHS
            or any(request.url.path.startswith(prefix) for prefix in PUBLIC_PREFIXES)
            or request.method == "OPTIONS"
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return self._unauthorized("Missing Bearer token")

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            request.state.user_id = payload["sub"]
            roles, capabilities = derive_roles_and_capabilities(payload)
            request.state.roles = roles
            request.state.capabilities = capabilities
        except jwt.ExpiredSignatureError:
            return self._unauthorized("Token expired")
        except jwt.InvalidTokenError as exc:
            return self._unauthorized(f"Invalid token: {exc}")

        return await call_next(request)
