"""Tier 1 quota helpers."""

from __future__ import annotations

from datetime import date, datetime, timezone

from config import settings
from services import supabase_client as db
from tier1.contracts import Tier1QuotaStatus


def utc_month_key(now: datetime | None = None) -> date:
    current = now or datetime.now(timezone.utc)
    current = current.astimezone(timezone.utc)
    return date(current.year, current.month, 1)


async def get_quota_status(user_id: str) -> Tier1QuotaStatus:
    month_key = utc_month_key()
    usage_row = await db.get_or_create_free_usage_month(user_id, month_key)
    reports_generated = int(usage_row.get("reports_generated") or 0)
    project_count = await db.get_active_project_count(user_id)

    reports_limit = int(settings.tier1_monthly_report_cap)
    project_limit = int(settings.tier1_project_cap)
    loc_cap = int(settings.tier1_loc_cap)

    return Tier1QuotaStatus(
        month_key=month_key,
        reports_generated=reports_generated,
        reports_limit=reports_limit,
        reports_remaining=max(0, reports_limit - reports_generated),
        project_count=project_count,
        project_limit=project_limit,
        loc_cap=loc_cap,
    )
