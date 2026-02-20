"""Structured telemetry helpers for orchestration runtime events."""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any
from uuid import UUID

from models.runtime import RuntimeMetric, RuntimeTelemetrySummary

logger = logging.getLogger("orchestration.runtime")

_MAX_BUFFER_SIZE = 2000
_metrics_lock = threading.Lock()
_metrics: list[RuntimeMetric] = []


def emit_runtime_metric(
    *,
    metric: str,
    value: int | float = 1,
    tags: dict[str, str] | None = None,
    fields: dict[str, Any] | None = None,
) -> None:
    """Emit a structured runtime telemetry log line."""
    record = RuntimeMetric(
        metric=metric,
        build_id=_parse_uuid(tags.get("build_id")) if tags else None,
        runtime_id=_parse_uuid(tags.get("runtime_id")) if tags else None,
        value=value,
        tags=tags or {},
        fields=fields or {},
    )
    _append_metric_record(record)

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


async def list_runtime_metrics(
    *,
    build_id: UUID | None = None,
    metric: str | None = None,
    limit: int = 200,
) -> list[RuntimeMetric]:
    _ = asyncio.get_running_loop()
    with _metrics_lock:
        rows = list(_metrics)
    if build_id is not None:
        rows = [row for row in rows if row.build_id == build_id]
    if metric is not None:
        rows = [row for row in rows if row.metric == metric]
    rows.sort(key=lambda row: row.emitted_at, reverse=True)
    return rows[: max(1, min(limit, 1000))]


async def summarize_runtime_metrics(build_id: UUID) -> RuntimeTelemetrySummary:
    rows = await list_runtime_metrics(build_id=build_id, limit=1000)
    summary = RuntimeTelemetrySummary(
        build_id=build_id,
        metric_count=len(rows),
        bootstrap_count=sum(1 for row in rows if row.metric == "runtime_bootstrap"),
        tick_count=sum(1 for row in rows if row.metric == "runtime_tick"),
        total_executed_nodes=int(
            sum(
                row.value
                for row in rows
                if row.metric == "runtime_tick" and isinstance(row.value, (int, float))
            )
        ),
    )
    if rows:
        latest = rows[0]
        summary.latest_runtime_id = latest.runtime_id
        summary.latest_status = (
            str(latest.fields.get("status")) if isinstance(latest.fields, dict) else None
        )
        summary.last_emitted_at = latest.emitted_at
    return summary


async def reset_runtime_metrics() -> None:
    _ = asyncio.get_running_loop()
    with _metrics_lock:
        _metrics.clear()


def _parse_uuid(raw: str | None) -> UUID | None:
    if raw is None:
        return None
    try:
        return UUID(raw)
    except (ValueError, TypeError):
        return None


def _append_metric_record(record: RuntimeMetric) -> None:
    with _metrics_lock:
        _metrics.append(record)
        if len(_metrics) > _MAX_BUFFER_SIZE:
            # Keep fixed-size in-memory buffer for local observability.
            del _metrics[: len(_metrics) - _MAX_BUFFER_SIZE]
