"""Structured telemetry helpers for orchestration runtime events."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("orchestration.runtime")


def emit_runtime_metric(
    *,
    metric: str,
    value: int | float = 1,
    tags: dict[str, str] | None = None,
    fields: dict[str, Any] | None = None,
) -> None:
    """Emit a structured runtime telemetry log line."""
    payload: dict[str, Any] = {
        "metric": metric,
        "value": value,
        "tags": tags or {},
        "fields": fields or {},
    }
    logger.info("runtime_metric %s", payload)


def emit_orchestration_event(
    *,
    event: str,
    build_id: str,
    node_id: str | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    """Emit a structured orchestration lifecycle event."""
    payload: dict[str, Any] = {
        "event": event,
        "build_id": build_id,
        "node_id": node_id,
        "data": data or {},
    }
    logger.info("orchestration_event %s", payload)
