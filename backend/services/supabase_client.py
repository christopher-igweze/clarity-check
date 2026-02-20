"""Supabase client for persisting scan reports, findings, and action items."""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from supabase import create_client, Client

from config import settings
from models.findings import (
    AuditReport,
    Finding,
    ActionItem,
    EducationCard,
)
from models.scan import ScanStatus


def _client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)


# ------------------------------------------------------------------ #
# Projects
# ------------------------------------------------------------------ #


async def get_or_create_project(
    user_id: str,
    repo_url: str,
    repo_name: str | None = None,
    vibe_prompt: str | None = None,
    project_charter: dict | None = None,
    latest_scan_tier: str = "deep",
) -> UUID:
    """Return the project ID for *repo_url*, creating the row if needed."""
    client = _client()
    existing = (
        client.table("projects")
        .select("id")
        .eq("user_id", str(user_id))
        .eq("repo_url", repo_url)
        .limit(1)
        .execute()
    )
    if existing.data:
        return UUID(existing.data[0]["id"])

    row = (
        client.table("projects")
        .insert(
            {
                "user_id": str(user_id),
                "repo_url": repo_url,
                "repo_name": repo_name,
                "vibe_prompt": vibe_prompt,
                "project_charter": project_charter,
                "latest_scan_tier": latest_scan_tier,
                "scan_count": 0,
            }
        )
        .execute()
    )
    return UUID(row.data[0]["id"])


async def get_project_by_repo_url(user_id: str, repo_url: str) -> dict | None:
    """Fetch the user's project row for a repo URL, if it exists."""
    client = _client()
    row = (
        client.table("projects")
        .select("*")
        .eq("user_id", str(user_id))
        .eq("repo_url", repo_url)
        .limit(1)
        .execute()
    )
    if not row.data:
        return None
    return row.data[0]


async def get_active_project_count(user_id: str) -> int:
    """Count projects currently tracked by a user."""
    client = _client()
    resp = (
        client.table("projects")
        .select("id", count="exact")
        .eq("user_id", str(user_id))
        .execute()
    )
    return int(resp.count or 0)


# ------------------------------------------------------------------ #
# Scan reports
# ------------------------------------------------------------------ #


async def create_scan_report(
    scan_id: UUID,
    project_id: UUID,
    user_id: str,
    scan_tier: str = "deep",
    project_intake: dict | None = None,
    primer_summary: str | None = None,
    audit_confidence: int | None = None,
) -> UUID:
    """Insert a new scan_reports row using the caller-supplied *scan_id*.

    The caller's ``scan_id`` becomes the row ``id`` so every downstream
    reference (update_scan_status, save_report, etc.) targets the same row.
    """
    client = _client()
    row = (
        client.table("scan_reports")
        .insert(
            {
                "id": str(scan_id),
                "project_id": str(project_id),
                "user_id": str(user_id),
                "scan_tier": scan_tier,
                "status": ScanStatus.pending.value,
                "project_intake": project_intake,
                "primer_summary": primer_summary,
                "audit_confidence": audit_confidence,
            }
        )
        .execute()
    )
    return UUID(row.data[0]["id"])


async def update_scan_status(scan_id: UUID, status: ScanStatus) -> None:
    client = _client()
    client.table("scan_reports").update({"status": status.value}).eq(
        "id", str(scan_id)
    ).execute()


async def save_report(
    scan_id: UUID,
    report: AuditReport,
    scan_tier: str = "deep",
    report_data_extra: dict | None = None,
) -> None:
    """Persist the final assembled report."""
    client = _client()
    report_data = report.model_dump(mode="json")
    if isinstance(report_data_extra, dict) and report_data_extra:
        report_data.update(report_data_extra)

    client.table("scan_reports").update(
        {
            "status": ScanStatus.completed.value,
            "health_score": report.health_score,
            "security_score": report.security_score,
            "reliability_score": report.reliability_score,
            "scalability_score": report.scalability_score,
            "audit_confidence": report.audit_confidence,
            "primer_summary": report.primer_summary,
            "evolution_report": report.evolution.model_dump(mode="json"),
            "report_data": report_data,
        }
    ).eq("id", str(scan_id)).execute()

    scan_row = (
        client.table("scan_reports")
        .select("project_id")
        .eq("id", str(scan_id))
        .limit(1)
        .execute()
    )
    if scan_row.data:
        project_id = scan_row.data[0]["project_id"]
        project_row = (
            client.table("projects")
            .select("scan_count")
            .eq("id", project_id)
            .limit(1)
            .execute()
        )
        current_scan_count = 0
        if project_row.data:
            current_scan_count = int(project_row.data[0].get("scan_count") or 0)
        client.table("projects").update(
            {
                "latest_health_score": report.health_score,
                "latest_scan_tier": scan_tier,
                "scan_count": current_scan_count + 1,
            }
        ).eq("id", project_id).execute()


# ------------------------------------------------------------------ #
# Primer cache
# ------------------------------------------------------------------ #


async def get_project_primer(project_id: UUID, repo_sha: str) -> dict | None:
    client = _client()
    row = (
        client.table("project_primers")
        .select("*")
        .eq("project_id", str(project_id))
        .eq("repo_sha", repo_sha)
        .limit(1)
        .execute()
    )
    if not row.data:
        return None
    return row.data[0]


async def save_project_primer(
    *,
    project_id: UUID,
    user_id: str,
    repo_sha: str,
    primer_json: dict,
    summary: str,
    confidence: int,
    failure_reason: str | None = None,
) -> None:
    client = _client()
    client.table("project_primers").upsert(
        {
            "project_id": str(project_id),
            "user_id": str(user_id),
            "repo_sha": repo_sha,
            "primer_json": primer_json,
            "summary": summary,
            "confidence": confidence,
            "failure_reason": failure_reason,
        },
        on_conflict="project_id,repo_sha",
    ).execute()


async def get_github_access_token(user_id: str) -> str | None:
    client = _client()
    row = (
        client.table("profiles")
        .select("github_access_token")
        .eq("user_id", str(user_id))
        .limit(1)
        .execute()
    )
    if not row.data:
        return None
    return row.data[0].get("github_access_token")


async def save_github_connection(
    *,
    user_id: str,
    access_token: str,
    github_username: str | None = None,
    avatar_url: str | None = None,
) -> None:
    """Persist GitHub OAuth credentials and profile metadata for a user."""
    client = _client()
    client.table("profiles").update(
        {
            "github_access_token": access_token,
            "github_username": github_username,
            "avatar_url": avatar_url,
        }
    ).eq("user_id", str(user_id)).execute()


async def clear_github_connection(*, user_id: str) -> None:
    """Remove stored GitHub OAuth credentials for a user."""
    client = _client()
    client.table("profiles").update(
        {
            "github_access_token": None,
            "github_username": None,
        }
    ).eq("user_id", str(user_id)).execute()


async def save_org_onboarding(*, user_id: str, payload: dict) -> None:
    client = _client()
    client.table("profiles").update(
        {
            "technical_level": payload.get("technical_level"),
            "explanation_style": payload.get("explanation_style"),
            "shipping_posture": payload.get("shipping_posture"),
            "tool_tags": payload.get("tool_tags") or [],
            "acquisition_source": payload.get("acquisition_source"),
            "acquisition_other": payload.get("acquisition_other"),
            "coding_agent_provider": payload.get("coding_agent_provider"),
            "coding_agent_model": payload.get("coding_agent_model"),
            "onboarding_complete": True,
        }
    ).eq("user_id", str(user_id)).execute()


async def is_onboarding_complete(user_id: str) -> bool:
    client = _client()
    row = (
        client.table("profiles")
        .select("onboarding_complete")
        .eq("user_id", str(user_id))
        .limit(1)
        .execute()
    )
    if not row.data:
        return False
    return bool(row.data[0].get("onboarding_complete"))


async def get_user_onboarding_preferences(user_id: str) -> dict | None:
    """Return stored onboarding preferences for report personalization."""
    client = _client()
    row = (
        client.table("profiles")
        .select(
            "technical_level,explanation_style,shipping_posture,tool_tags,acquisition_source,acquisition_other,coding_agent_provider,coding_agent_model,onboarding_complete"
        )
        .eq("user_id", str(user_id))
        .limit(1)
        .execute()
    )
    if not row.data:
        return None
    return row.data[0]


# ------------------------------------------------------------------ #
# Tier 1 usage + caching + artifacts
# ------------------------------------------------------------------ #


async def get_or_create_free_usage_month(user_id: str, month_key: date) -> dict:
    """Get or create monthly free-tier usage row."""
    client = _client()
    iso_month = month_key.isoformat()

    existing = (
        client.table("free_usage_monthly")
        .select("*")
        .eq("user_id", str(user_id))
        .eq("month_key", iso_month)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]

    created = (
        client.table("free_usage_monthly")
        .insert(
            {
                "user_id": str(user_id),
                "month_key": iso_month,
                "reports_generated": 0,
            }
        )
        .execute()
    )
    return created.data[0]


async def increment_free_reports_generated(user_id: str, month_key: date) -> int:
    """Increment free-tier reports_generated counter and return new value."""
    row = await get_or_create_free_usage_month(user_id, month_key)
    current = int(row.get("reports_generated") or 0)
    next_value = current + 1

    client = _client()
    client.table("free_usage_monthly").update(
        {"reports_generated": next_value}
    ).eq("id", row["id"]).execute()
    return next_value


async def get_project_index(project_id: UUID, repo_sha: str) -> dict | None:
    """Return active cached project index for a commit SHA."""
    client = _client()
    now_iso = datetime.now(timezone.utc).isoformat()
    row = (
        client.table("project_indexes")
        .select("*")
        .eq("project_id", str(project_id))
        .eq("repo_sha", repo_sha)
        .gt("expires_at", now_iso)
        .limit(1)
        .execute()
    )
    if not row.data:
        return None
    return row.data[0]


async def upsert_project_index(
    *,
    project_id: UUID,
    user_id: str,
    repo_sha: str,
    loc_total: int,
    file_count: int,
    index_json: dict,
    expires_at: datetime,
) -> dict:
    """Create or update a project index cache row."""
    client = _client()
    row = (
        client.table("project_indexes")
        .upsert(
            {
                "project_id": str(project_id),
                "user_id": str(user_id),
                "repo_sha": repo_sha,
                "loc_total": int(loc_total),
                "file_count": int(file_count),
                "index_json": index_json,
                "expires_at": expires_at.astimezone(timezone.utc).isoformat(),
            },
            on_conflict="project_id,repo_sha",
        )
        .execute()
    )
    return row.data[0]


async def save_report_artifact(
    *,
    scan_report_id: UUID,
    project_id: UUID,
    user_id: str,
    content: str,
    artifact_type: str = "markdown",
    expires_at: datetime,
) -> dict:
    """Persist a TTL-bound report artifact."""
    client = _client()
    row = (
        client.table("report_artifacts")
        .upsert(
            {
                "scan_report_id": str(scan_report_id),
                "project_id": str(project_id),
                "user_id": str(user_id),
                "artifact_type": artifact_type,
                "content": content,
                "expires_at": expires_at.astimezone(timezone.utc).isoformat(),
            },
            on_conflict="scan_report_id,artifact_type",
        )
        .execute()
    )
    return row.data[0]


async def get_report_artifact(
    scan_report_id: UUID, user_id: str, artifact_type: str = "markdown"
) -> dict | None:
    """Fetch a non-expired report artifact for the requesting user."""
    client = _client()
    now_iso = datetime.now(timezone.utc).isoformat()
    row = (
        client.table("report_artifacts")
        .select("*")
        .eq("scan_report_id", str(scan_report_id))
        .eq("user_id", str(user_id))
        .eq("artifact_type", artifact_type)
        .gt("expires_at", now_iso)
        .limit(1)
        .execute()
    )
    if not row.data:
        return None
    return row.data[0]


async def delete_expired_report_artifacts() -> int:
    """Delete expired report artifacts and return number deleted."""
    client = _client()
    now_iso = datetime.now(timezone.utc).isoformat()
    expired = (
        client.table("report_artifacts")
        .select("id")
        .lte("expires_at", now_iso)
        .execute()
    )
    count = len(expired.data or [])
    if count:
        client.table("report_artifacts").delete().lte("expires_at", now_iso).execute()
    return count


async def delete_expired_project_indexes() -> int:
    """Delete expired project index cache rows and return number deleted."""
    client = _client()
    now_iso = datetime.now(timezone.utc).isoformat()
    expired = (
        client.table("project_indexes")
        .select("id")
        .lte("expires_at", now_iso)
        .execute()
    )
    count = len(expired.data or [])
    if count:
        client.table("project_indexes").delete().lte("expires_at", now_iso).execute()
    return count


# ------------------------------------------------------------------ #
# Findings (raw scanner output → action_items table)
# ------------------------------------------------------------------ #


async def save_findings(
    scan_id: UUID, project_id: UUID, user_id: str, findings: list[Finding]
) -> None:
    """Bulk-insert action_items rows from Scanner findings."""
    if not findings:
        return
    client = _client()
    rows = [
        {
            "scan_report_id": str(scan_id),
            "project_id": str(project_id),
            "user_id": str(user_id),
            "title": f.title,
            "description": f.description,
            "category": f.category.value,
            "severity": f.severity.value,
            "source": f.source.value,
            "file_path": f.file_path,
            "line_number": f.line_number,
        }
        for f in findings
    ]
    client.table("action_items").insert(rows).execute()


# ------------------------------------------------------------------ #
# Action items (Planner output)
# ------------------------------------------------------------------ #


async def save_action_items(
    scan_id: UUID, project_id: UUID, user_id: str, items: list[ActionItem]
) -> None:
    """Persist prioritised action items from the Planner.

    Each row uses the ActionItem's model ``id`` so that save_education
    can target a specific row later.
    """
    if not items:
        return
    client = _client()
    rows = [
        {
            "id": str(item.id),
            "scan_report_id": str(scan_id),
            "project_id": str(project_id),
            "user_id": str(user_id),
            "title": item.title,
            "description": item.description,
            "category": item.category.value,
            "severity": item.severity.value,
            "file_path": item.file_path,
            "line_number": item.line_number,
        }
        for item in items
    ]
    client.table("action_items").insert(rows).execute()


# ------------------------------------------------------------------ #
# Education cards (Educator output → update existing action_items)
# ------------------------------------------------------------------ #


async def save_education(
    scan_id: UUID,
    project_id: UUID,
    user_id: str,
    cards: list[EducationCard],
) -> None:
    """Attach education text to specific action_items rows."""
    if not cards:
        return
    client = _client()
    for card in cards:
        client.table("action_items").update(
            {
                "why_it_matters": card.why_it_matters,
                "cto_perspective": card.cto_perspective,
            }
        ).eq("id", str(card.action_item_id)).execute()
