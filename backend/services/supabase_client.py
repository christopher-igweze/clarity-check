"""Supabase client for persisting scan reports, findings, and action items."""

from __future__ import annotations

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
    scan_tier: str = "deep",
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
                "latest_scan_tier": scan_tier,
                "scan_count": 1,
            }
        )
        .execute()
    )
    return UUID(row.data[0]["id"])


# ------------------------------------------------------------------ #
# Scan reports
# ------------------------------------------------------------------ #


async def create_scan_report(
    scan_id: UUID, project_id: UUID, user_id: str, scan_tier: str
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


async def save_report(scan_id: UUID, report: AuditReport) -> None:
    """Persist the final assembled report."""
    client = _client()
    client.table("scan_reports").update(
        {
            "status": ScanStatus.completed.value,
            "health_score": report.health_score,
            "security_score": report.security_score,
            "reliability_score": report.reliability_score,
            "scalability_score": report.scalability_score,
            "report_data": report.model_dump(mode="json"),
        }
    ).eq("id", str(scan_id)).execute()


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
