"""GET /api/status/{scan_id} — SSE stream of audit progress.

The frontend connects to this endpoint immediately after calling
POST /api/audit and receives a real-time stream of agent logs,
findings, probe results, and the final report.
"""

from __future__ import annotations

import asyncio
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException
from sse_starlette.sse import EventSourceResponse

from models.agent_log import SSEEventType
from api.routes._sse import event_buses

logger = logging.getLogger(__name__)
router = APIRouter()


async def _event_generator(scan_id: UUID):
    """Yield SSE events as agents produce them."""
    bus = event_buses.get(scan_id)
    if bus is None:
        yield {
            "event": "error",
            "data": json.dumps({"message": "Unknown scan_id"}),
        }
        return

    cursor = 0
    idle_ticks = 0
    max_idle = 600  # 10 minutes with no new events → close

    while True:
        if cursor < len(bus):
            # New events available
            for entry in bus[cursor:]:
                yield {
                    "event": entry.event_type.value,
                    "data": json.dumps(
                        entry.model_dump(mode="json"), default=str
                    ),
                }

                # If scan is done or errored, close the stream
                if entry.event_type in (
                    SSEEventType.scan_complete,
                    SSEEventType.scan_error,
                ):
                    return

            cursor = len(bus)
            idle_ticks = 0
        else:
            idle_ticks += 1
            if idle_ticks >= max_idle:
                yield {
                    "event": "timeout",
                    "data": json.dumps({"message": "Stream timed out"}),
                }
                return

        await asyncio.sleep(1)


@router.get("/status/{scan_id}")
async def stream_status(scan_id: UUID, request: Request):
    """Stream audit events for a given scan via SSE."""
    if scan_id not in event_buses:
        raise HTTPException(status_code=404, detail="Scan not found")

    return EventSourceResponse(
        _event_generator(scan_id),
        media_type="text/event-stream",
    )
