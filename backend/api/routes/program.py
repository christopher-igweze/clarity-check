"""Program routes for Weeks 7-16 implementation tracks with e2e coverage."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from api.middleware.authorization import require_capability
from api.middleware.rate_limit import limiter, rate_limit_string
from models.program import (
    CampaignRunIngestRequest,
    GoLiveDecision,
    GoLiveDecisionRequest,
    IdempotentCheckpointRequest,
    IdempotentCheckpointResult,
    PlatformWebhookResponse,
    PolicyCheckRequest,
    PolicyCheckResult,
    PolicyProfile,
    PolicyProfileRequest,
    ReleaseChecklist,
    ReleaseChecklistRequest,
    RollbackDrill,
    RollbackDrillRequest,
    SecretCreateRequest,
    SecretMetadata,
    SecretRef,
    SloSummary,
    ValidationCampaign,
    ValidationCampaignRequest,
)
from orchestration.benchmark_harness import ValidationBenchmarkReport
from orchestration.program_store import program_store
from services.ephemeral_coordination import CoordinationUnavailableError

router = APIRouter()


# Week 7
@router.post("/v1/program/campaigns", response_model=ValidationCampaign)
@router.post("/v1/program/week7/campaigns", response_model=ValidationCampaign)
@limiter.limit(rate_limit_string())
async def create_validation_campaign(
    request_body: ValidationCampaignRequest,
    request: Request,
) -> ValidationCampaign:
    require_capability(request, "program.validation.write")
    return await program_store.create_campaign(
        user_id=request.state.user_id,
        request=request_body,
    )


@router.get("/v1/program/campaigns/{campaign_id}", response_model=ValidationCampaign)
@router.get("/v1/program/week7/campaigns/{campaign_id}", response_model=ValidationCampaign)
async def get_validation_campaign(campaign_id: UUID, request: Request) -> ValidationCampaign:
    require_capability(request, "program.validation.read")
    campaign = await program_store.get_campaign(campaign_id)
    if campaign is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "campaign_not_found", "message": "Campaign not found."},
        )
    return campaign


# Week 8
@router.post("/v1/program/campaigns/{campaign_id}/runs")
@router.post("/v1/program/week8/campaigns/{campaign_id}/runs")
@limiter.limit(rate_limit_string())
async def ingest_campaign_run(
    campaign_id: UUID,
    request_body: CampaignRunIngestRequest,
    request: Request,
) -> dict:
    require_capability(request, "program.validation.write")
    _ = request.state.user_id
    try:
        run = await program_store.ingest_campaign_run(campaign_id, request_body)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "campaign_not_found", "message": "Campaign not found."},
        ) from exc
    return {"status": "accepted", "run_id": run.run_id}


@router.get(
    "/v1/program/campaigns/{campaign_id}/report",
    response_model=ValidationBenchmarkReport,
)
@router.get(
    "/v1/program/week8/campaigns/{campaign_id}/report",
    response_model=ValidationBenchmarkReport,
)
async def campaign_report(campaign_id: UUID, request: Request) -> ValidationBenchmarkReport:
    require_capability(request, "program.validation.read")
    try:
        return await program_store.campaign_report(campaign_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "campaign_not_found", "message": "Campaign not found."},
        ) from exc


# Week 9
@router.post("/v1/program/policy-profiles", response_model=PolicyProfile)
@router.post("/v1/program/week9/policy-profiles", response_model=PolicyProfile)
@limiter.limit(rate_limit_string())
async def create_policy_profile(
    request_body: PolicyProfileRequest,
    request: Request,
) -> PolicyProfile:
    require_capability(request, "program.policy.write")
    return await program_store.create_policy_profile(
        user_id=request.state.user_id,
        request=request_body,
    )


@router.post("/v1/program/policy-check", response_model=PolicyCheckResult)
@router.post("/v1/program/week9/policy-check", response_model=PolicyCheckResult)
@limiter.limit(rate_limit_string())
async def policy_check(
    request_body: PolicyCheckRequest,
    request: Request,
) -> PolicyCheckResult:
    require_capability(request, "program.policy.check")
    _ = request.state.user_id
    try:
        return await program_store.evaluate_policy(request_body)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "policy_profile_not_found", "message": "Policy profile not found."},
        ) from exc


# Week 10
@router.post("/v1/program/secrets", response_model=SecretRef)
@router.post("/v1/program/week10/secrets", response_model=SecretRef)
@limiter.limit(rate_limit_string())
async def create_secret(
    request_body: SecretCreateRequest,
    request: Request,
) -> SecretRef:
    require_capability(request, "program.secrets.write")
    return await program_store.store_secret(
        user_id=request.state.user_id,
        request=request_body,
    )


@router.get("/v1/program/secrets", response_model=list[SecretRef])
@router.get("/v1/program/week10/secrets", response_model=list[SecretRef])
async def list_secrets(request: Request) -> list[SecretRef]:
    require_capability(request, "program.secrets.read")
    return await program_store.list_secrets(user_id=request.state.user_id)


@router.get("/v1/program/secrets/{secret_id}", response_model=SecretMetadata)
@router.get("/v1/program/week10/secrets/{secret_id}", response_model=SecretMetadata)
async def get_secret_metadata(secret_id: UUID, request: Request) -> SecretMetadata:
    require_capability(request, "program.secrets.read")
    try:
        return await program_store.get_secret_metadata(
            secret_id=secret_id,
            user_id=request.state.user_id,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "secret_not_found", "message": "Secret not found."},
        ) from exc


# Week 11
@router.post("/v1/program/webhook/ingest", response_model=PlatformWebhookResponse)
@router.post("/v1/program/week11/webhook/ingest", response_model=PlatformWebhookResponse)
@limiter.limit(rate_limit_string())
async def ingest_platform_webhook(request: Request) -> PlatformWebhookResponse:
    require_capability(request, "program.webhook.ingest")
    nonce = request.headers.get("X-Platform-Nonce", "").strip()
    timestamp_str = request.headers.get("X-Platform-Timestamp", "").strip()
    signature = request.headers.get("X-Platform-Signature", "").strip()
    if not nonce or not timestamp_str or not signature:
        raise HTTPException(
            status_code=400,
            detail={"code": "webhook_headers_missing", "message": "Missing webhook security headers."},
        )
    try:
        timestamp = int(timestamp_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "timestamp_invalid", "message": "Timestamp must be an integer."},
        ) from exc
    body = await request.body()
    try:
        return await program_store.ingest_platform_webhook(
            body=body,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
        )
    except CoordinationUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "coordination_unavailable",
                "message": str(exc),
            },
        ) from exc
    except ValueError as exc:
        msg = str(exc)
        code = "webhook_rejected"
        status_code = 401
        if msg == "nonce_replay_detected":
            code = "webhook_replay_detected"
            status_code = 409
        if msg == "timestamp_out_of_window":
            code = "webhook_timestamp_invalid"
            status_code = 401
        if msg == "signature_invalid":
            code = "webhook_signature_invalid"
            status_code = 401
        raise HTTPException(
            status_code=status_code,
            detail={"code": code, "message": msg},
        ) from exc


# Week 12
@router.post(
    "/v1/program/idempotent-checkpoints",
    response_model=IdempotentCheckpointResult,
)
@router.post(
    "/v1/program/week12/idempotent-checkpoints",
    response_model=IdempotentCheckpointResult,
)
@limiter.limit(rate_limit_string())
async def idempotent_checkpoint(
    request_body: IdempotentCheckpointRequest,
    request: Request,
) -> IdempotentCheckpointResult:
    require_capability(request, "program.runtime.write")
    _ = request.state.user_id
    try:
        return await program_store.create_idempotent_checkpoint(
            build_id=request_body.build_id,
            idempotency_key=request_body.idempotency_key,
            reason=request_body.reason,
        )
    except CoordinationUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "coordination_unavailable", "message": str(exc)},
        ) from exc
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "build_not_found", "message": "Build not found."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_idempotency_request", "message": str(exc)},
        ) from exc


# Week 13
@router.get("/v1/program/slo-summary", response_model=SloSummary)
@router.get("/v1/program/week13/slo-summary", response_model=SloSummary)
async def get_slo_summary(request: Request) -> SloSummary:
    require_capability(request, "program.runtime.read")
    return await program_store.slo_summary(user_id=request.state.user_id)


# Week 14
@router.post("/v1/program/checklist", response_model=ReleaseChecklist)
@router.post("/v1/program/week14/checklist", response_model=ReleaseChecklist)
@limiter.limit(rate_limit_string())
async def upsert_release_checklist(
    request_body: ReleaseChecklistRequest,
    request: Request,
) -> ReleaseChecklist:
    require_capability(request, "program.release.write")
    return await program_store.upsert_release_checklist(
        user_id=request.state.user_id,
        request=request_body,
    )


@router.get("/v1/program/checklist/{release_id}", response_model=ReleaseChecklist)
@router.get("/v1/program/week14/checklist/{release_id}", response_model=ReleaseChecklist)
async def get_release_checklist(release_id: str, request: Request) -> ReleaseChecklist:
    require_capability(request, "program.release.read")
    row = await program_store.get_release_checklist(release_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "checklist_not_found", "message": "Release checklist not found."},
        )
    return row


# Week 15
@router.post("/v1/program/rollback-drills", response_model=RollbackDrill)
@router.post("/v1/program/week15/rollback-drills", response_model=RollbackDrill)
@limiter.limit(rate_limit_string())
async def upsert_rollback_drill(
    request_body: RollbackDrillRequest,
    request: Request,
) -> RollbackDrill:
    require_capability(request, "program.release.write")
    return await program_store.upsert_rollback_drill(
        user_id=request.state.user_id,
        request=request_body,
    )


@router.get("/v1/program/rollback-drills/{release_id}", response_model=RollbackDrill)
@router.get("/v1/program/week15/rollback-drills/{release_id}", response_model=RollbackDrill)
async def get_rollback_drill(release_id: str, request: Request) -> RollbackDrill:
    require_capability(request, "program.release.read")
    row = await program_store.get_rollback_drill(release_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "rollback_drill_not_found", "message": "Rollback drill not found."},
        )
    return row


# Week 16
@router.post("/v1/program/go-live-decision", response_model=GoLiveDecision)
@router.post("/v1/program/week16/go-live-decision", response_model=GoLiveDecision)
@limiter.limit(rate_limit_string())
async def decide_go_live(
    request_body: GoLiveDecisionRequest,
    request: Request,
) -> GoLiveDecision:
    require_capability(request, "program.release.write")
    return await program_store.decide_go_live(
        user_id=request.state.user_id,
        request=request_body,
    )


@router.get("/v1/program/go-live-decision/{release_id}", response_model=GoLiveDecision)
@router.get("/v1/program/week16/go-live-decision/{release_id}", response_model=GoLiveDecision)
async def get_go_live_decision(release_id: str, request: Request) -> GoLiveDecision:
    require_capability(request, "program.release.read")
    row = await program_store.get_go_live_decision(release_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "go_live_decision_not_found", "message": "Decision not found."},
        )
    return row
