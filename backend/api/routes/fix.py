"""POST /api/fix — Trigger auto-fix for an action item (PAID feature).

This is the revenue feature.  It spins up a sandbox, runs Agent_Builder
with the Planner's fix instructions, verifies with tests, and pushes a PR.

Stub implementation — the full auto-fix loop will be wired in Phase 3.
"""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Request, HTTPException

from models.scan import FixRequest, FixResponse
from api.middleware.rate_limit import limiter, rate_limit_string

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/fix", response_model=FixResponse)
@limiter.limit(rate_limit_string())
async def trigger_fix(
    request_body: FixRequest,
    request: Request,
) -> FixResponse:
    """Accept an action_item_id and kick off the auto-fix loop.

    Phase 3 implementation will:
    1. Look up the action item and its fix_steps from the Planner
    2. Provision a sandbox and clone the repo
    3. Run Agent_Builder with the fix instructions
    4. Agent_Builder edits code, runs tests, self-corrects
    5. Agent_Security reviews the diff
    6. If approved, push a PR to the user's GitHub
    7. Save the trajectory for fine-tuning
    """
    fix_id = uuid4()

    # TODO: Phase 3 — wire up the full auto-fix loop
    # For now, return a stub response indicating the feature is queued

    return FixResponse(
        fix_attempt_id=fix_id,
        status="pending",
        message=(
            "Auto-fix is queued. This feature is under active development. "
            "The fix loop (edit → test → verify → PR) will be wired in Phase 3."
        ),
    )
