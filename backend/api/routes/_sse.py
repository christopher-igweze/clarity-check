"""Shared SSE event bus used by audit routes and the status endpoint.

Each scan gets a list that agents append ``AgentLogEntry`` objects to.
The ``/api/status/{scan_id}`` endpoint reads from this list and streams
events to the client using Server-Sent Events.
"""

from __future__ import annotations

from uuid import UUID

from models.agent_log import AgentLogEntry

# scan_id → ordered list of events produced by agents
event_buses: dict[UUID, list[AgentLogEntry]] = {}
