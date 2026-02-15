"""POST /api/audit — Start a full audit of a GitHub repository.

Kicks off the orchestrator pipeline in a background task and returns
immediately with the scan_id.  The client streams progress via
GET /api/status/{scan_id}.
"""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from slowapi import Limiter

from models.scan import AuditRequest, AuditResponse, ScanStatus
from models.agent_log import AgentLogEntry
from agents.orchestrator import AuditOrchestrator
from services import supabase_client as db
from api.middleware.rate_limit import limiter, rate_limit_string
from api.routes._sse import event_buses

logger = logging.getLogger(__name__)
router = APIRouter()


async def _run_audit(
    scan_id: UUID,
    request: AuditRequest,
    user_id: str,
    github_token: str | None = None,
) -> None:
    """Background task that runs the full audit pipeline."""
    bus = event_buses.get(scan_id)

    def emit(entry: AgentLogEntry) -> None:
        if bus is not None:
            bus.append(entry)

    try:
        await db.update_scan_status(scan_id, ScanStatus.scanning)

        orchestrator = AuditOrchestrator(
            scan_id=scan_id,
            repo_url=str(request.repo_url),
            scan_tier=request.scan_tier,
            emit=emit,
            vibe_prompt=request.vibe_prompt,
            project_charter=request.project_charter,
            github_token=github_token,
        )

        report = await orchestrator.run()

        # Persist to Supabase
        await db.save_report(scan_id, report)

        # Persist findings and action items
        project_id = scan_id  # simplified — in prod, look up from projects table
        await db.save_findings(
            scan_id, project_id, UUID(user_id), report.findings
        )
        await db.save_action_items(
            scan_id, project_id, UUID(user_id), report.action_items
        )
        await db.save_education(
            scan_id, project_id, UUID(user_id), report.education_cards
        )

    except Exception:
        logger.exception("Audit background task failed for scan %s", scan_id)
        await db.update_scan_status(scan_id, ScanStatus.failed)


@router.post("/audit", response_model=AuditResponse)
@limiter.limit(rate_limit_string())
async def start_audit(
    request_body: AuditRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> AuditResponse:
    """Accept a GitHub URL and kick off a full audit."""
    user_id: str = request.state.user_id
    scan_id = uuid4()

    # Create the SSE event bus before the background task starts
    event_buses[scan_id] = []

    # Create the scan_reports row
    # In a real implementation, we'd look up or create the project first
    try:
        await db.create_scan_report(
            project_id=scan_id,  # simplified
            user_id=UUID(user_id),
            scan_tier=request_body.scan_tier.value,
        )
    except Exception:
        logger.exception("Failed to create scan report row")
        raise HTTPException(status_code=500, detail="Failed to create scan")

    background_tasks.add_task(
        _run_audit, scan_id, request_body, user_id
    )

    return AuditResponse(scan_id=scan_id)
