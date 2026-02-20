"""GitHub OAuth exchange and connection lifecycle routes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter, rate_limit_string
from config import settings
from services import supabase_client as db

router = APIRouter()


class GithubOAuthRequest(BaseModel):
    action: Literal["get_auth_url", "exchange_code", "disconnect"]
    code: str | None = None
    redirect_uri: str | None = None
    state: str | None = None


class GithubOAuthResponse(BaseModel):
    auth_url: str | None = None
    github_username: str | None = None
    avatar_url: str | None = None
    connected: bool = False
    message: str | None = None


def _oauth_not_configured() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "code": "github_oauth_not_configured",
            "message": "GitHub OAuth is not configured on the backend.",
        },
    )


def _state_secret() -> str:
    return settings.github_oauth_state_secret or settings.supabase_jwt_secret


def _ensure_oauth_configured() -> None:
    if not settings.github_client_id or not settings.github_client_secret:
        raise _oauth_not_configured()


def _encode_state(user_id: str, redirect_uri: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "redirect_uri": redirect_uri,
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.github_oauth_state_ttl_minutes)).timestamp()
        ),
    }
    return jwt.encode(payload, _state_secret(), algorithm="HS256")


def _decode_state(state: str) -> dict:
    try:
        payload = jwt.decode(state, _state_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "oauth_state_expired",
                "message": "GitHub OAuth state has expired. Start the flow again.",
            },
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "oauth_state_invalid",
                "message": "GitHub OAuth state is invalid.",
            },
        ) from exc
    return payload


async def _exchange_code_for_access_token(
    *,
    code: str,
    redirect_uri: str,
    state: str,
) -> str:
    _ensure_oauth_configured()
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "state": state,
            },
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "github_token_exchange_failed",
                "message": "GitHub token exchange failed.",
            },
        )

    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "github_token_missing",
                "message": data.get("error_description")
                or "GitHub did not return an access token.",
            },
        )
    return token


async def _fetch_github_profile(access_token: str) -> tuple[str | None, str | None]:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
            },
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "github_profile_fetch_failed",
                "message": "Failed to fetch GitHub profile after OAuth exchange.",
            },
        )
    data = resp.json()
    return data.get("login"), data.get("avatar_url")


@router.post("/github-oauth", response_model=GithubOAuthResponse)
@limiter.limit(rate_limit_string())
async def github_oauth(request_body: GithubOAuthRequest, request: Request) -> GithubOAuthResponse:
    user_id: str = request.state.user_id

    if request_body.action == "disconnect":
        await db.clear_github_connection(user_id=user_id)
        return GithubOAuthResponse(connected=False, message="GitHub disconnected.")

    if request_body.action == "get_auth_url":
        if not request_body.redirect_uri:
            raise HTTPException(
                status_code=400,
                detail={"code": "redirect_uri_required", "message": "redirect_uri is required."},
            )
        _ensure_oauth_configured()
        state = _encode_state(user_id=user_id, redirect_uri=request_body.redirect_uri)
        query = urlencode(
            {
                "client_id": settings.github_client_id,
                "redirect_uri": request_body.redirect_uri,
                "scope": settings.github_oauth_scope,
                "state": state,
            }
        )
        return GithubOAuthResponse(
            auth_url=f"https://github.com/login/oauth/authorize?{query}",
            connected=False,
        )

    if request_body.action == "exchange_code":
        if not request_body.code:
            raise HTTPException(
                status_code=400,
                detail={"code": "code_required", "message": "code is required."},
            )
        if not request_body.redirect_uri:
            raise HTTPException(
                status_code=400,
                detail={"code": "redirect_uri_required", "message": "redirect_uri is required."},
            )
        if not request_body.state:
            raise HTTPException(
                status_code=400,
                detail={"code": "state_required", "message": "state is required."},
            )

        state_payload = _decode_state(request_body.state)
        if state_payload.get("sub") != user_id:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "oauth_state_user_mismatch",
                    "message": "GitHub OAuth state does not belong to this user.",
                },
            )
        if state_payload.get("redirect_uri") != request_body.redirect_uri:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "oauth_state_redirect_mismatch",
                    "message": "GitHub OAuth redirect URI mismatch.",
                },
            )

        access_token = await _exchange_code_for_access_token(
            code=request_body.code,
            redirect_uri=request_body.redirect_uri,
            state=request_body.state,
        )
        github_username, avatar_url = await _fetch_github_profile(access_token)
        await db.save_github_connection(
            user_id=user_id,
            access_token=access_token,
            github_username=github_username,
            avatar_url=avatar_url,
        )
        return GithubOAuthResponse(
            github_username=github_username,
            avatar_url=avatar_url,
            connected=True,
            message="GitHub connected.",
        )

    raise HTTPException(
        status_code=400,
        detail={"code": "action_invalid", "message": "Unsupported GitHub OAuth action."},
    )

