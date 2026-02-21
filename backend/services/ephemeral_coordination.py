"""Ephemeral coordination helpers (nonce replay + idempotency cache).

Uses Redis when configured, with in-process fallback for local/test environments.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis_async  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - optional dependency
    redis_async = None


class EphemeralCoordinator:
    def __init__(self, redis_url: str | None) -> None:
        self._lock = asyncio.Lock()
        self._redis_url = redis_url
        self._redis = None
        self._nonce_seen: dict[str, int] = {}
        self._idempotency_cache: dict[str, tuple[int, dict[str, Any]]] = {}

    async def _redis_client(self):
        if not self._redis_url or redis_async is None:
            return None
        if self._redis is None:
            try:
                self._redis = redis_async.from_url(self._redis_url, encoding="utf-8", decode_responses=True)
            except Exception:
                logger.warning("Redis unavailable; falling back to in-process ephemeral coordination.")
                self._redis = None
        return self._redis

    async def claim_nonce(self, nonce: str, *, ttl_seconds: int) -> bool:
        redis_client = await self._redis_client()
        key = f"cp:nonce:{nonce}"
        if redis_client is not None:
            try:
                claimed = await redis_client.set(key, str(int(time.time())), ex=ttl_seconds, nx=True)
                return bool(claimed)
            except Exception:
                logger.warning("Redis nonce claim failed; using in-process fallback.")

        now_ts = int(time.time())
        async with self._lock:
            expired = [token for token, seen in self._nonce_seen.items() if (now_ts - seen) > ttl_seconds]
            for token in expired:
                self._nonce_seen.pop(token, None)
            if nonce in self._nonce_seen:
                return False
            self._nonce_seen[nonce] = now_ts
            return True

    async def get_idempotency(self, key: str, *, ttl_seconds: int) -> dict[str, Any] | None:
        redis_client = await self._redis_client()
        redis_key = f"cp:idempotency:{key}"
        if redis_client is not None:
            try:
                raw = await redis_client.get(redis_key)
                if raw:
                    payload = json.loads(raw)
                    if isinstance(payload, dict):
                        return payload
                return None
            except Exception:
                logger.warning("Redis idempotency read failed; using in-process fallback.")

        now_ts = int(time.time())
        async with self._lock:
            stale = [
                token for token, (created_ts, _) in self._idempotency_cache.items()
                if (now_ts - created_ts) > ttl_seconds
            ]
            for token in stale:
                self._idempotency_cache.pop(token, None)
            row = self._idempotency_cache.get(key)
            if row is None:
                return None
            return dict(row[1])

    async def set_idempotency(
        self,
        key: str,
        *,
        payload: dict[str, Any],
        ttl_seconds: int,
    ) -> None:
        redis_client = await self._redis_client()
        redis_key = f"cp:idempotency:{key}"
        if redis_client is not None:
            try:
                await redis_client.set(redis_key, json.dumps(payload), ex=ttl_seconds)
                return
            except Exception:
                logger.warning("Redis idempotency write failed; using in-process fallback.")

        async with self._lock:
            self._idempotency_cache[key] = (int(time.time()), dict(payload))


ephemeral_coordinator = EphemeralCoordinator(settings.redis_url)
