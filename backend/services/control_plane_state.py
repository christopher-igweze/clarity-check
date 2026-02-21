"""Durable control-plane state snapshots backed by Supabase with graceful fallback."""

from __future__ import annotations

import logging
from typing import Any

from supabase import Client, create_client

from config import settings

logger = logging.getLogger(__name__)

_TABLE_NAME = "control_plane_state"


def _supabase_client() -> Client | None:
    if not settings.control_plane_use_supabase:
        return None
    if not settings.supabase_url or not settings.supabase_service_key:
        return None
    try:
        return create_client(settings.supabase_url, settings.supabase_service_key)
    except Exception:
        logger.exception("Failed to initialize Supabase client for control-plane state.")
        return None


async def load_state_snapshot(state_key: str) -> dict[str, Any] | None:
    """Load a control-plane snapshot from Supabase.

    Returns ``None`` when the row does not exist or Supabase is unavailable.
    """
    client = _supabase_client()
    if client is None:
        return None
    try:
        row = (
            client.table(_TABLE_NAME)
            .select("state_payload")
            .eq("state_key", state_key)
            .limit(1)
            .execute()
        )
        if not row.data:
            return None
        payload = row.data[0].get("state_payload")
        if isinstance(payload, dict):
            return payload
        return None
    except Exception:
        logger.warning(
            "Control-plane state load skipped (Supabase unavailable): state_key=%s",
            state_key,
        )
        return None


async def save_state_snapshot(state_key: str, payload: dict[str, Any]) -> bool:
    """Persist a control-plane snapshot to Supabase.

    Returns ``True`` when saved to Supabase, ``False`` when unavailable.
    """
    client = _supabase_client()
    if client is None:
        return False
    try:
        client.table(_TABLE_NAME).upsert(
            {
                "state_key": state_key,
                "state_payload": payload,
            },
            on_conflict="state_key",
        ).execute()
        return True
    except Exception:
        logger.warning(
            "Control-plane state save skipped (Supabase unavailable): state_key=%s",
            state_key,
        )
        return False
