"""Tier-aware audit routes.

`POST /api/audit` starts either:
- Tier 1 deterministic pipeline (free tier), or
- existing deep multi-agent pipeline (feature-flag fallback).
"""

from __future__ import annotations

import logging
from datetime import date, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Request, HTTPException, Query

from agents.orchestrator import AuditOrchestrator
from api.middleware.rate_limit import limiter, rate_limit_string
from api.routes._sse import event_buses
from config import settings
from models.agent_log import AgentLogEntry, AgentName, LogLevel, SSEEventType
from models.scan import AuditRequest, AuditResponse, ScanStatus
from services import supabase_client as db
from services.github import get_head_sha, get_repo_info, parse_repo_url
from tier1.indexer import DeterministicIndexer
from tier1.orchestrator import Tier1Orchestrator
from tier1.quota import get_quota_status, utc_month_key

logger = logging.getLogger(__name__)
router = APIRouter()

_LIMIT_STATUS = 403
_CLEANUP_EVERY_N_SCANS = 5
_scan_start_counter = 0


def _limit_exception(code: str, message: str, extra: dict | None = None) -> HTTPException:
    payload = {"code": code, "message": message}
    if extra:
        payload.update(extra)
    return HTTPException(status_code=_LIMIT_STATUS, detail=payload)


async def cleanup_tier1_expired() -> None:
    """Purge expired free-tier artifacts/indexes."""
    try:
        deleted_artifacts = await db.delete_expired_report_artifacts()
        deleted_indexes = await db.delete_expired_project_indexes()
        if deleted_artifacts or deleted_indexes:
            logger.info(
                "Tier1 cleanup removed artifacts=%s indexes=%s",
                deleted_artifacts,
                deleted_indexes,
            )
    except Exception:
        logger.exception("Tier1 cleanup failed")


async def _maybe_cleanup_tier1() -> None:
    global _scan_start_counter
    _scan_start_counter += 1
    if _scan_start_counter % _CLEANUP_EVERY_N_SCANS == 0:
        await cleanup_tier1_expired()


async def _run_deep_audit(
    scan_id: UUID,
    project_id: UUID,
    request: AuditRequest,
    user_id: str,
    github_token: str | None = None,
) -> None:
    """Background task that runs the existing deep audit pipeline."""
    bus = event_buses.get(scan_id)

    def emit(entry: AgentLogEntry) -> None:
        if bus is not None:
            bus.append(entry)

    try:
        await db.update_scan_status(scan_id, ScanStatus.scanning)

        orchestrator = AuditOrchestrator(
            scan_id=scan_id,
            repo_url=str(request.repo_url),
            emit=emit,
            vibe_prompt=request.vibe_prompt,
            project_charter=request.project_charter,
            project_intake=request.project_intake,
            primer=request.primer,
            github_token=github_token,
        )

        report = await orchestrator.run()

        await db.save_report(scan_id, report, scan_tier="deep")
        await db.save_findings(scan_id, project_id, user_id, report.findings)
        await db.save_action_items(scan_id, project_id, user_id, report.action_items)
        await db.save_education(scan_id, project_id, user_id, report.education_cards)
    except Exception:
        logger.exception("Deep audit background task failed for scan %s", scan_id)
        await db.update_scan_status(scan_id, ScanStatus.failed)


async def _run_tier1_audit(
    scan_id: UUID,
    project_id: UUID,
    request: AuditRequest,
    user_id: str,
    month_key: date,
    github_token: str | None = None,
) -> None:
    """Background task that runs Tier 1 deterministic audit pipeline."""
    bus = event_buses.get(scan_id)

    def emit(entry: AgentLogEntry) -> None:
        if bus is not None:
            bus.append(entry)

    def emit_scan_error(message: str) -> None:
        emit(
            AgentLogEntry(
                event_type=SSEEventType.scan_error,
                agent=AgentName.orchestrator,
                message=message,
                level=LogLevel.error,
            )
        )

    try:
        await db.update_scan_status(scan_id, ScanStatus.scanning)
        usage_before = await db.get_or_create_free_usage_month(user_id, month_key)
        reports_generated_before = int(usage_before.get("reports_generated") or 0)
        user_preferences = await db.get_user_onboarding_preferences(user_id)

        emit(
            AgentLogEntry(
                event_type=SSEEventType.agent_start,
                agent=AgentName.orchestrator,
                message="Tier 1 preflight passed. Starting deterministic pipeline.",
                level=LogLevel.info,
            )
        )

        orchestrator = Tier1Orchestrator(
            scan_id=scan_id,
            repo_url=str(request.repo_url),
            project_id=project_id,
            user_id=user_id,
            project_intake=request.project_intake.model_dump(mode="json"),
            primer=request.primer,
            emit=emit,
            github_token=github_token,
            user_preferences=user_preferences,
            run_context={
                "reports_generated_before": reports_generated_before,
                "report_limit": settings.tier1_monthly_report_cap,
            },
        )

        result = await orchestrator.run()
        report = result["audit_report"]
        artifact = result["artifact"]
        scores = result["scores"]

        tier1_metadata = {
            "run_details": result.get("run_details") or {},
            "index_facts": result.get("index_facts") or {},
            "git_metadata": result.get("git_metadata") or {},
            "summary": artifact.summary_json or {},
            "artifact_expires_at": artifact.expires_at.astimezone(timezone.utc).isoformat(),
            "model_used": artifact.model_used,
            "fallback_used": artifact.fallback_used,
        }

        await db.save_report(
            scan_id,
            report,
            scan_tier="free",
            report_data_extra={"tier1": tier1_metadata},
        )
        await db.save_findings(scan_id, project_id, user_id, report.findings)

        await db.save_report_artifact(
            scan_report_id=scan_id,
            project_id=project_id,
            user_id=user_id,
            content=artifact.markdown,
            artifact_type="markdown",
            expires_at=artifact.expires_at,
        )
        await db.save_report_artifact(
            scan_report_id=scan_id,
            project_id=project_id,
            user_id=user_id,
            content=artifact.agent_markdown,
            artifact_type="agent_markdown",
            expires_at=artifact.expires_at,
        )
        if artifact.pdf_base64:
            await db.save_report_artifact(
                scan_report_id=scan_id,
                project_id=project_id,
                user_id=user_id,
                content=artifact.pdf_base64,
                artifact_type="pdf",
                expires_at=artifact.expires_at,
            )

        reports_generated = await db.increment_free_reports_generated(user_id, month_key)
        quota_remaining = max(0, settings.tier1_monthly_report_cap - reports_generated)

        emit(
            AgentLogEntry(
                event_type=SSEEventType.scan_complete,
                agent=AgentName.orchestrator,
                message=f"Tier 1 scan complete. Health score: {scores['health_score']}/100",
                level=LogLevel.success,
                data={
                    "health_score": scores["health_score"],
                    "security_score": scores["security_score"],
                    "reliability_score": scores["reliability_score"],
                    "scalability_score": scores["scalability_score"],
                    "findings_count": len(result["actionable_findings"]),
                    "quota_remaining": quota_remaining,
                    "report_artifact_available": True,
                    "report_artifact_types": [
                        t
                        for t in ("markdown", "agent_markdown", "pdf")
                        if t != "pdf" or artifact.pdf_base64
                    ],
                },
            )
        )
    except Exception:
        logger.exception("Tier1 audit background task failed for scan %s", scan_id)
        emit_scan_error("Tier 1 scan failed before report generation.")
        await db.update_scan_status(scan_id, ScanStatus.failed)


async def _tier1_preflight(
    request_body: AuditRequest,
    user_id: str,
    github_token: str | None,
) -> dict:
    if not await db.is_onboarding_complete(user_id):
        raise _limit_exception(
            "onboarding_required",
            "Organization onboarding is required before starting scans.",
        )

    existing_project = await db.get_project_by_repo_url(user_id, str(request_body.repo_url))
    project_count = await db.get_active_project_count(user_id)
    is_new_project = existing_project is None

    if is_new_project and project_count >= settings.tier1_project_cap:
        raise _limit_exception(
            "limit_projects_exceeded",
            "Free tier project limit reached.",
            {
                "project_count": project_count,
                "project_limit": settings.tier1_project_cap,
            },
        )

    month_key = utc_month_key()
    usage_row = await db.get_or_create_free_usage_month(user_id, month_key)
    reports_generated = int(usage_row.get("reports_generated") or 0)
    if reports_generated >= settings.tier1_monthly_report_cap:
        raise _limit_exception(
            "limit_reports_exceeded",
            "Free tier monthly report limit reached.",
            {
                "reports_generated": reports_generated,
                "reports_limit": settings.tier1_monthly_report_cap,
            },
        )

    owner, repo = await parse_repo_url(str(request_body.repo_url))
    repo_info = await get_repo_info(owner, repo, github_token)
    repo_sha = await get_head_sha(owner, repo, repo_info.default_branch, github_token)

    indexer = DeterministicIndexer()
    index_payload = await indexer.build_or_reuse(
        project_id=UUID(existing_project["id"]) if existing_project else None,
        user_id=user_id if existing_project else None,
        repo_url=str(request_body.repo_url),
        clone_url=repo_info.clone_url,
        repo_sha=repo_sha,
        github_token=github_token,
    )
    loc_total = int(index_payload.get("loc_total") or 0)

    if loc_total > settings.tier1_loc_cap:
        raise _limit_exception(
            "limit_loc_exceeded",
            "Repository LOC exceeds the free tier cap.",
            {
                "loc_total": loc_total,
                "loc_cap": settings.tier1_loc_cap,
            },
        )

    return {
        "existing_project": existing_project,
        "month_key": month_key,
        "repo_name": repo_info.full_name,
        "repo_sha": repo_sha,
        "loc_total": loc_total,
        "file_count": int(index_payload.get("file_count") or 0),
        "reports_remaining": settings.tier1_monthly_report_cap - reports_generated,
    }


@router.post("/audit", response_model=AuditResponse)
@limiter.limit(rate_limit_string())
async def start_audit(
    request_body: AuditRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> AuditResponse:
    """Accept a GitHub URL and kick off an audit."""
    user_id: str = request.state.user_id
    scan_id = uuid4()

    event_buses[scan_id] = []

    try:
        github_token = await db.get_github_access_token(user_id)

        if settings.tier1_enabled:
            await _maybe_cleanup_tier1()
            preflight = await _tier1_preflight(request_body, user_id, github_token)

            project_id = (
                UUID(preflight["existing_project"]["id"])
                if preflight["existing_project"]
                else await db.get_or_create_project(
                    user_id=user_id,
                    repo_url=str(request_body.repo_url),
                    repo_name=preflight["repo_name"],
                    vibe_prompt=request_body.vibe_prompt,
                    project_charter=request_body.project_charter,
                    latest_scan_tier="free",
                )
            )

            await db.create_scan_report(
                scan_id=scan_id,
                project_id=project_id,
                user_id=user_id,
                scan_tier="free",
                project_intake=request_body.project_intake.model_dump(mode="json"),
                primer_summary=(request_body.primer.summary if request_body.primer else None),
                audit_confidence=(request_body.primer.confidence if request_body.primer else None),
            )

            background_tasks.add_task(
                _run_tier1_audit,
                scan_id,
                project_id,
                request_body,
                user_id,
                preflight["month_key"],
                github_token,
            )

            return AuditResponse(
                scan_id=scan_id,
                tier="free",
                quota_remaining=preflight["reports_remaining"],
            )

        # Fallback: existing deep pipeline
        project_id = await db.get_or_create_project(
            user_id=user_id,
            repo_url=str(request_body.repo_url),
            vibe_prompt=request_body.vibe_prompt,
            project_charter=request_body.project_charter,
        )

        await db.create_scan_report(
            scan_id=scan_id,
            project_id=project_id,
            user_id=user_id,
            scan_tier="deep",
            project_intake=request_body.project_intake.model_dump(mode="json"),
            primer_summary=(request_body.primer.summary if request_body.primer else None),
            audit_confidence=(request_body.primer.confidence if request_body.primer else None),
        )
    except HTTPException:
        # preserve machine-readable limit code payload
        raise
    except Exception:
        logger.exception("Failed to create scan report row")
        raise HTTPException(status_code=500, detail="Failed to create scan")

    background_tasks.add_task(
        _run_deep_audit,
        scan_id,
        project_id,
        request_body,
        user_id,
        github_token,
    )

    return AuditResponse(scan_id=scan_id, tier="deep")


@router.get("/limits")
async def get_limits(request: Request) -> dict:
    """Return free-tier monthly limits and current usage."""
    user_id: str = request.state.user_id
    quota = await get_quota_status(user_id)

    return {
        "tier": "free",
        "month_key": quota.month_key.isoformat(),
        "reports_generated": quota.reports_generated,
        "reports_limit": quota.reports_limit,
        "reports_remaining": quota.reports_remaining,
        "project_count": quota.project_count,
        "project_limit": quota.project_limit,
        "loc_cap": quota.loc_cap,
    }


@router.get("/report-artifacts/{scan_id}")
async def get_report_artifact(
    scan_id: UUID,
    request: Request,
    artifact_type: str = Query(default="markdown"),
) -> dict:
    """Fetch an active report artifact for a completed scan."""
    allowed = {"markdown", "agent_markdown", "pdf"}
    if artifact_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "report_artifact_type_invalid",
                "message": f"Unsupported artifact_type '{artifact_type}'. Allowed: {sorted(allowed)}",
            },
        )

    user_id: str = request.state.user_id
    artifact = await db.get_report_artifact(scan_id, user_id, artifact_type)
    if not artifact:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "report_artifact_missing",
                "message": "Report artifact is missing or expired. Run a new scan.",
            },
        )

    mime_type = "text/markdown"
    content_encoding = "utf-8"
    filename = f"clarity-check-report-{scan_id}.md"
    if artifact_type == "agent_markdown":
        filename = f"clarity-check-agent-{scan_id}.md"
    elif artifact_type == "pdf":
        mime_type = "application/pdf"
        content_encoding = "base64"
        filename = f"clarity-check-report-{scan_id}.pdf"

    return {
        "scan_id": str(scan_id),
        "artifact_type": artifact.get("artifact_type", artifact_type),
        "content": artifact.get("content", ""),
        "expires_at": artifact.get("expires_at"),
        "mime_type": mime_type,
        "content_encoding": content_encoding,
        "filename": filename,
    }
