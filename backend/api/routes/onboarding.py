"""Org onboarding routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from models.onboarding import OrgOnboardingPayload
from services import supabase_client as db

router = APIRouter()


class OnboardingResponse(BaseModel):
    status: str = "ok"
    message: str = "Org onboarding saved"


@router.post("/onboarding/org", response_model=OnboardingResponse)
async def save_org_onboarding(
    request_body: OrgOnboardingPayload,
    request: Request,
) -> OnboardingResponse:
    user_id: str = request.state.user_id
    await db.save_org_onboarding(user_id=user_id, payload=request_body.model_dump(mode="json"))
    return OnboardingResponse()

