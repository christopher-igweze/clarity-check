"""Webhook ingestion routes with fail-closed signature + replay checks."""

from __future__ import annotations

import asyncio
import hmac
import logging
import time
from hashlib import sha256

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

_seen_deliveries: dict[str, int] = {}
_deliveries_lock = asyncio.Lock()


class WebhookResponse(BaseModel):
    status: str = "ok"
    message: str = "Webhook accepted."
    event: str | None = None
    action: str | None = None
    delivery_id: str | None = None


def _webhook_not_configured() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "code": "webhook_not_configured",
            "message": "GitHub webhook secret is not configured.",
        },
    )


def _verify_github_signature(*, body: bytes, signature: str) -> bool:
    secret = settings.github_webhook_secret
    if not secret:
        raise _webhook_not_configured()
    if not signature.startswith("sha256="):
        return False

    expected = "sha256=" + hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _register_delivery(delivery_id: str) -> bool:
    """Return False when a duplicate delivery ID is observed inside replay window."""
    now_ts = int(time.time())
    ttl_seconds = max(60, int(settings.webhook_replay_window_seconds))

    async with _deliveries_lock:
        expired_ids = [
            key
            for key, seen_ts in _seen_deliveries.items()
            if (now_ts - seen_ts) > ttl_seconds
        ]
        for key in expired_ids:
            _seen_deliveries.pop(key, None)

        if delivery_id in _seen_deliveries:
            return False

        _seen_deliveries[delivery_id] = now_ts
        return True


@router.post("/webhook/github", response_model=WebhookResponse)
async def github_webhook(request: Request) -> WebhookResponse:
    signature = request.headers.get("X-Hub-Signature-256", "")
    delivery_id = request.headers.get("X-GitHub-Delivery")
    event = request.headers.get("X-GitHub-Event", "unknown")

    if not delivery_id:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "delivery_id_missing",
                "message": "Missing X-GitHub-Delivery header.",
            },
        )

    body = await request.body()
    if not _verify_github_signature(body=body, signature=signature):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "webhook_signature_invalid",
                "message": "Webhook signature verification failed.",
            },
        )

    is_fresh = await _register_delivery(delivery_id)
    if not is_fresh:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "webhook_replay_detected",
                "message": "Duplicate webhook delivery detected.",
            },
        )

    action: str | None = None
    try:
        payload = await request.json()
        if isinstance(payload, dict):
            raw_action = payload.get("action")
            if isinstance(raw_action, str):
                action = raw_action
    except Exception:
        payload = None

    logger.info(
        "GitHub webhook accepted event=%s action=%s delivery=%s",
        event,
        action or "-",
        delivery_id,
    )

    return WebhookResponse(event=event, action=action, delivery_id=delivery_id)

