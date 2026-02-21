"""Normalized control-plane persistence adapters for Supabase tables."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import logging
from typing import Any

from supabase import Client, create_client

from config import settings

logger = logging.getLogger(__name__)


def _client_or_none() -> Client | None:
    if not settings.control_plane_use_supabase:
        return None
    if not settings.supabase_url or not settings.supabase_service_key:
        return None
    try:
        return create_client(settings.supabase_url, settings.supabase_service_key)
    except Exception:
        logger.exception("Failed to initialize Supabase client for normalized control-plane tables.")
        return None


def _parse_ts(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


async def load_build_store_entities() -> dict[str, Any] | None:
    client = _client_or_none()
    if client is None:
        return None
    try:
        build_rows = client.table("build_runs").select("*").order("created_at", desc=False).execute()
    except Exception:
        logger.warning("Failed loading build_runs table for control-plane rehydration.")
        return None

    rows = build_rows.data or []
    if not rows:
        return None

    payload: dict[str, Any] = {"builds": {}, "events": {}, "checkpoints": {}}
    build_ids: list[str] = []
    for row in rows:
        build_id = str(row.get("build_id"))
        if not build_id:
            continue
        build_ids.append(build_id)
        payload["builds"][build_id] = {
            "build_id": build_id,
            "created_by": str(row.get("user_id") or ""),
            "repo_url": str(row.get("repo_url") or ""),
            "objective": str(row.get("objective") or ""),
            "status": str(row.get("status") or "pending"),
            "created_at": _parse_ts(row.get("created_at")),
            "updated_at": _parse_ts(row.get("updated_at")),
            "dag": _as_list(row.get("dag")),
            "task_runs": [],
            "replan_history": [],
            "debt_items": [],
            "policy_violations": [],
            "state_transitions": [],
            "gate_history": [],
            "metadata": _as_dict(row.get("metadata")),
        }
        payload["events"][build_id] = []
        payload["checkpoints"][build_id] = []

    if not build_ids:
        return None

    try:
        event_rows = (
            client.table("build_events")
            .select("*")
            .in_("build_id", build_ids)
            .order("created_at", desc=False)
            .execute()
        )
        for row in event_rows.data or []:
            build_id = str(row.get("build_id") or "")
            if build_id not in payload["builds"]:
                continue
            event_payload = _as_dict(row.get("payload"))
            event_type = str(row.get("event_type") or "")
            event = {
                "event_type": event_type,
                "build_id": build_id,
                "timestamp": _parse_ts(row.get("created_at")),
                "payload": event_payload,
            }
            payload["events"][build_id].append(event)

            if event_type == "BUILD_STATUS_CHANGED":
                transition = {
                    "transition_id": event_payload.get("transition_id"),
                    "from_status": event_payload.get("from_status"),
                    "to_status": event_payload.get("to_status"),
                    "reason": event_payload.get("reason"),
                    "source": event_payload.get("source") or "system",
                    "created_at": _parse_ts(row.get("created_at")),
                }
                if all(transition.values()):
                    payload["builds"][build_id]["state_transitions"].append(transition)

            if event_type in {"MERGE_GATE", "TEST_GATE", "POLICY_GATE"}:
                decision = {
                    "decision_id": event_payload.get("decision_id"),
                    "build_id": build_id,
                    "gate": event_payload.get("gate") or event_type,
                    "status": event_payload.get("status"),
                    "reason": event_payload.get("reason"),
                    "node_id": event_payload.get("node_id"),
                    "created_at": _parse_ts(row.get("created_at")),
                }
                if decision.get("decision_id") and decision.get("status") and decision.get("reason"):
                    payload["builds"][build_id]["gate_history"].append(decision)
    except Exception:
        logger.warning("Failed loading build_events table for control-plane rehydration.")

    try:
        task_rows = (
            client.table("build_tasks")
            .select("*")
            .in_("build_id", build_ids)
            .order("started_at", desc=False)
            .execute()
        )
        for row in task_rows.data or []:
            build_id = str(row.get("build_id") or "")
            if build_id not in payload["builds"]:
                continue
            payload["builds"][build_id]["task_runs"].append(
                {
                    "task_run_id": row.get("task_run_id"),
                    "node_id": row.get("node_id"),
                    "attempt": int(row.get("attempt") or 1),
                    "status": row.get("status"),
                    "started_at": _parse_ts(row.get("started_at")),
                    "finished_at": _parse_ts(row.get("finished_at"))
                    if row.get("finished_at")
                    else None,
                    "error": row.get("error"),
                }
            )
    except Exception:
        logger.warning("Failed loading build_tasks table for control-plane rehydration.")

    try:
        replan_rows = (
            client.table("replan_decisions")
            .select("*")
            .in_("build_id", build_ids)
            .order("created_at", desc=False)
            .execute()
        )
        for row in replan_rows.data or []:
            build_id = str(row.get("build_id") or "")
            if build_id not in payload["builds"]:
                continue
            payload["builds"][build_id]["replan_history"].append(
                {
                    "decision_id": row.get("decision_id"),
                    "action": row.get("action"),
                    "reason": row.get("reason"),
                    "created_at": _parse_ts(row.get("created_at")),
                    "replacement_nodes": _as_list(row.get("replacement_nodes")),
                }
            )
    except Exception:
        logger.warning("Failed loading replan_decisions table for control-plane rehydration.")

    try:
        debt_rows = (
            client.table("debt_items")
            .select("*")
            .in_("build_id", build_ids)
            .order("created_at", desc=False)
            .execute()
        )
        for row in debt_rows.data or []:
            build_id = str(row.get("build_id") or "")
            if build_id not in payload["builds"]:
                continue
            payload["builds"][build_id]["debt_items"].append(
                {
                    "debt_id": row.get("debt_id"),
                    "node_id": row.get("node_id"),
                    "summary": row.get("summary"),
                    "severity": row.get("severity") or "medium",
                    "created_at": _parse_ts(row.get("created_at")),
                }
            )
    except Exception:
        logger.warning("Failed loading debt_items table for control-plane rehydration.")

    try:
        policy_rows = (
            client.table("policy_violations")
            .select("*")
            .in_("build_id", build_ids)
            .order("created_at", desc=False)
            .execute()
        )
        for row in policy_rows.data or []:
            build_id = str(row.get("build_id") or "")
            if build_id not in payload["builds"]:
                continue
            payload["builds"][build_id]["policy_violations"].append(
                {
                    "violation_id": row.get("violation_id"),
                    "code": row.get("code"),
                    "message": row.get("message"),
                    "source": row.get("source"),
                    "blocking": bool(row.get("blocking", True)),
                    "created_at": _parse_ts(row.get("created_at")),
                }
            )
    except Exception:
        logger.warning("Failed loading policy_violations table for control-plane rehydration.")

    try:
        checkpoint_rows = (
            client.table("build_checkpoints")
            .select("*")
            .in_("build_id", build_ids)
            .order("created_at", desc=False)
            .execute()
        )
        for row in checkpoint_rows.data or []:
            build_id = str(row.get("build_id") or "")
            if build_id not in payload["checkpoints"]:
                continue
            payload["checkpoints"][build_id].append(
                {
                    "checkpoint_id": row.get("checkpoint_id"),
                    "build_id": build_id,
                    "status": row.get("status"),
                    "reason": row.get("reason"),
                    "event_cursor": int(row.get("event_cursor") or 0),
                    "created_at": _parse_ts(row.get("created_at")),
                }
            )
    except Exception:
        logger.warning("Failed loading build_checkpoints table for control-plane rehydration.")

    return payload


async def save_build_store_entities(payload: dict[str, Any]) -> bool:
    client = _client_or_none()
    if client is None:
        return False

    builds = _as_dict(payload.get("builds"))
    if not builds:
        return True

    build_rows: list[dict[str, Any]] = []
    build_owner: dict[str, str] = {}
    for build_id, raw in builds.items():
        row = _as_dict(raw)
        owner = str(row.get("created_by") or "")
        build_owner[str(build_id)] = owner
        build_rows.append(
            {
                "build_id": str(build_id),
                "user_id": owner,
                "repo_url": str(row.get("repo_url") or ""),
                "objective": str(row.get("objective") or ""),
                "status": str(row.get("status") or "pending"),
                "dag": _as_list(row.get("dag")),
                "metadata": _as_dict(row.get("metadata")),
                "created_at": _parse_ts(row.get("created_at")),
                "updated_at": _parse_ts(row.get("updated_at")),
            }
        )

    try:
        client.table("build_runs").upsert(build_rows, on_conflict="build_id").execute()
    except Exception:
        logger.warning("Failed persisting build_runs normalized table.")
        return False

    build_ids = list(builds.keys())
    for table_name in [
        "build_events",
        "build_tasks",
        "replan_decisions",
        "debt_items",
        "policy_violations",
        "build_checkpoints",
    ]:
        try:
            client.table(table_name).delete().in_("build_id", build_ids).execute()
        except Exception:
            logger.warning("Failed clearing %s normalized rows before upsert.", table_name)

    events = _as_dict(payload.get("events"))
    event_rows: list[dict[str, Any]] = []
    for build_id, rows in events.items():
        owner = build_owner.get(str(build_id), "")
        for row in _as_list(rows):
            event = _as_dict(row)
            event_rows.append(
                {
                    "build_id": str(build_id),
                    "user_id": owner,
                    "event_type": str(event.get("event_type") or ""),
                    "payload": _as_dict(event.get("payload")),
                    "created_at": _parse_ts(event.get("timestamp")),
                }
            )
    if event_rows:
        try:
            client.table("build_events").insert(event_rows).execute()
        except Exception:
            logger.warning("Failed persisting build_events normalized rows.")

    task_rows: list[dict[str, Any]] = []
    replan_rows: list[dict[str, Any]] = []
    debt_rows: list[dict[str, Any]] = []
    policy_rows: list[dict[str, Any]] = []
    for build_id, raw in builds.items():
        build = _as_dict(raw)
        owner = build_owner.get(str(build_id), "")

        for task in _as_list(build.get("task_runs")):
            item = _as_dict(task)
            task_rows.append(
                {
                    "task_run_id": item.get("task_run_id"),
                    "build_id": str(build_id),
                    "user_id": owner,
                    "node_id": item.get("node_id"),
                    "attempt": int(item.get("attempt") or 1),
                    "status": item.get("status"),
                    "error": item.get("error"),
                    "started_at": _parse_ts(item.get("started_at")),
                    "finished_at": _parse_ts(item.get("finished_at"))
                    if item.get("finished_at")
                    else None,
                }
            )

        for decision in _as_list(build.get("replan_history")):
            item = _as_dict(decision)
            replan_rows.append(
                {
                    "decision_id": item.get("decision_id"),
                    "build_id": str(build_id),
                    "user_id": owner,
                    "action": item.get("action"),
                    "reason": item.get("reason"),
                    "replacement_nodes": _as_list(item.get("replacement_nodes")),
                    "created_at": _parse_ts(item.get("created_at")),
                }
            )

        for debt in _as_list(build.get("debt_items")):
            item = _as_dict(debt)
            debt_rows.append(
                {
                    "debt_id": item.get("debt_id"),
                    "build_id": str(build_id),
                    "user_id": owner,
                    "node_id": item.get("node_id"),
                    "summary": item.get("summary"),
                    "severity": item.get("severity") or "medium",
                    "created_at": _parse_ts(item.get("created_at")),
                }
            )

        for violation in _as_list(build.get("policy_violations")):
            item = _as_dict(violation)
            policy_rows.append(
                {
                    "violation_id": item.get("violation_id"),
                    "build_id": str(build_id),
                    "user_id": owner,
                    "code": item.get("code"),
                    "message": item.get("message"),
                    "source": item.get("source"),
                    "blocking": bool(item.get("blocking", True)),
                    "created_at": _parse_ts(item.get("created_at")),
                }
            )

    if task_rows:
        try:
            client.table("build_tasks").insert(task_rows).execute()
        except Exception:
            logger.warning("Failed persisting build_tasks normalized rows.")
    if replan_rows:
        try:
            client.table("replan_decisions").insert(replan_rows).execute()
        except Exception:
            logger.warning("Failed persisting replan_decisions normalized rows.")
    if debt_rows:
        try:
            client.table("debt_items").insert(debt_rows).execute()
        except Exception:
            logger.warning("Failed persisting debt_items normalized rows.")
    if policy_rows:
        try:
            client.table("policy_violations").insert(policy_rows).execute()
        except Exception:
            logger.warning("Failed persisting policy_violations normalized rows.")

    checkpoints = _as_dict(payload.get("checkpoints"))
    checkpoint_rows: list[dict[str, Any]] = []
    for build_id, rows in checkpoints.items():
        owner = build_owner.get(str(build_id), "")
        for checkpoint in _as_list(rows):
            row = _as_dict(checkpoint)
            checkpoint_rows.append(
                {
                    "checkpoint_id": row.get("checkpoint_id"),
                    "build_id": str(build_id),
                    "user_id": owner,
                    "status": row.get("status"),
                    "reason": row.get("reason"),
                    "event_cursor": int(row.get("event_cursor") or 0),
                    "created_at": _parse_ts(row.get("created_at")),
                }
            )
    if checkpoint_rows:
        try:
            client.table("build_checkpoints").insert(checkpoint_rows).execute()
        except Exception:
            logger.warning("Failed persisting build_checkpoints normalized rows.")

    return True


async def load_program_store_entities() -> dict[str, Any] | None:
    client = _client_or_none()
    if client is None:
        return None

    payload: dict[str, Any] = {
        "campaigns": {},
        "campaign_runs": {},
        "policy_profiles": {},
        "secrets": {},
        "seen_nonces": {},
        "idempotent_checkpoints": {},
        "release_checklists": {},
        "rollback_drills": {},
        "go_live_decisions": {},
    }
    loaded_any = False

    try:
        campaign_rows = client.table("validation_campaigns").select("*").execute()
        for row in campaign_rows.data or []:
            loaded_any = True
            campaign_id = str(row.get("campaign_id"))
            payload["campaigns"][campaign_id] = {
                "campaign_id": campaign_id,
                "name": row.get("name"),
                "repos": _as_list(row.get("repos")),
                "runs_per_repo": int(row.get("runs_per_repo") or 3),
                "created_by": row.get("user_id"),
                "created_at": _parse_ts(row.get("created_at")),
            }
            payload["campaign_runs"][campaign_id] = {}
    except Exception:
        logger.warning("Failed loading validation_campaigns for control-plane rehydration.")

    try:
        run_rows = client.table("validation_campaign_runs").select("*").execute()
        for row in run_rows.data or []:
            loaded_any = True
            campaign_id = str(row.get("campaign_id"))
            if campaign_id not in payload["campaign_runs"]:
                payload["campaign_runs"][campaign_id] = {}
            run_id = str(row.get("run_id"))
            payload["campaign_runs"][campaign_id][run_id] = {
                "repo": row.get("repo"),
                "language": row.get("language"),
                "run_id": run_id,
                "status": row.get("status"),
                "duration_ms": int(row.get("duration_ms") or 0),
                "findings_total": int(row.get("findings_total") or 0),
            }
    except Exception:
        logger.warning("Failed loading validation_campaign_runs for control-plane rehydration.")

    try:
        profile_rows = client.table("program_policy_profiles").select("*").execute()
        for row in profile_rows.data or []:
            loaded_any = True
            profile_id = str(row.get("profile_id"))
            payload["policy_profiles"][profile_id] = {
                "profile_id": profile_id,
                "name": row.get("name"),
                "blocked_commands": _as_list(row.get("blocked_commands")),
                "restricted_paths": _as_list(row.get("restricted_paths")),
                "created_by": row.get("user_id"),
                "created_at": _parse_ts(row.get("created_at")),
            }
    except Exception:
        logger.warning("Failed loading program_policy_profiles for control-plane rehydration.")

    try:
        secret_rows = client.table("program_secrets").select("*").execute()
        for row in secret_rows.data or []:
            loaded_any = True
            secret_id = str(row.get("secret_id"))
            payload["secrets"][secret_id] = {
                "secret_id": secret_id,
                "name": row.get("name"),
                "encrypted_value": row.get("encrypted_value"),
                "created_by": row.get("user_id"),
                "created_at": _parse_ts(row.get("created_at")),
            }
    except Exception:
        logger.warning("Failed loading program_secrets for control-plane rehydration.")

    try:
        checklist_rows = client.table("release_checklists").select("*").execute()
        for row in checklist_rows.data or []:
            loaded_any = True
            release_id = str(row.get("release_id"))
            payload["release_checklists"][release_id] = {
                "release_id": release_id,
                "security_review": bool(row.get("security_review")),
                "slo_dashboard": bool(row.get("slo_dashboard")),
                "rollback_tested": bool(row.get("rollback_tested")),
                "docs_complete": bool(row.get("docs_complete")),
                "runbooks_ready": bool(row.get("runbooks_ready")),
                "updated_by": row.get("user_id"),
                "updated_at": _parse_ts(row.get("updated_at")),
            }
    except Exception:
        logger.warning("Failed loading release_checklists for control-plane rehydration.")

    try:
        rollback_rows = client.table("rollback_drills").select("*").execute()
        for row in rollback_rows.data or []:
            loaded_any = True
            release_id = str(row.get("release_id"))
            payload["rollback_drills"][release_id] = {
                "release_id": release_id,
                "passed": bool(row.get("passed")),
                "duration_minutes": int(row.get("duration_minutes") or 0),
                "issues_found": _as_list(row.get("issues_found")),
                "updated_by": row.get("user_id"),
                "updated_at": _parse_ts(row.get("updated_at")),
            }
    except Exception:
        logger.warning("Failed loading rollback_drills for control-plane rehydration.")

    try:
        decision_rows = client.table("go_live_decisions").select("*").execute()
        for row in decision_rows.data or []:
            loaded_any = True
            release_id = str(row.get("release_id"))
            payload["go_live_decisions"][release_id] = {
                "release_id": release_id,
                "status": row.get("status"),
                "reasons": _as_list(row.get("reasons")),
                "decided_by": row.get("user_id"),
                "decided_at": _parse_ts(row.get("decided_at")),
            }
    except Exception:
        logger.warning("Failed loading go_live_decisions for control-plane rehydration.")

    try:
        idem_rows = client.table("program_idempotent_checkpoints").select("*").execute()
        for row in idem_rows.data or []:
            loaded_any = True
            build_id = str(row.get("build_id"))
            idem_key = str(row.get("idempotency_key") or "")
            if not idem_key:
                continue
            payload["idempotent_checkpoints"][f"{build_id}::{idem_key}"] = {
                "created_ts": int(row.get("created_ts") or 0),
                "user_id": row.get("user_id"),
                "checkpoint": {
                    "checkpoint_id": row.get("checkpoint_id"),
                    "build_id": build_id,
                    "status": row.get("status"),
                    "reason": row.get("reason"),
                    "event_cursor": 0,
                    "created_at": _parse_ts(row.get("created_at")),
                },
            }
    except Exception:
        logger.warning("Failed loading program_idempotent_checkpoints for control-plane rehydration.")

    return payload if loaded_any else None


async def save_program_store_entities(payload: dict[str, Any]) -> bool:
    client = _client_or_none()
    if client is None:
        return False

    campaigns = _as_dict(payload.get("campaigns"))
    campaign_rows: list[dict[str, Any]] = []
    for campaign_id, raw in campaigns.items():
        row = _as_dict(raw)
        campaign_rows.append(
            {
                "campaign_id": str(campaign_id),
                "user_id": row.get("created_by"),
                "name": row.get("name"),
                "repos": _as_list(row.get("repos")),
                "runs_per_repo": int(row.get("runs_per_repo") or 3),
                "created_at": _parse_ts(row.get("created_at")),
                "updated_at": _parse_ts(row.get("created_at")),
            }
        )
    if campaign_rows:
        try:
            client.table("validation_campaigns").upsert(
                campaign_rows,
                on_conflict="campaign_id",
            ).execute()
        except Exception:
            logger.warning("Failed persisting validation_campaigns normalized rows.")

    campaign_runs = _as_dict(payload.get("campaign_runs"))
    campaign_ids = [str(key) for key in campaign_runs.keys()]
    if campaign_ids:
        try:
            client.table("validation_campaign_runs").delete().in_("campaign_id", campaign_ids).execute()
        except Exception:
            logger.warning("Failed clearing validation_campaign_runs before insert.")
    run_rows: list[dict[str, Any]] = []
    for campaign_id, runs in campaign_runs.items():
        campaign = _as_dict(campaigns.get(campaign_id))
        owner = campaign.get("created_by")
        for run in _as_dict(runs).values():
            item = _as_dict(run)
            run_rows.append(
                {
                    "campaign_id": str(campaign_id),
                    "user_id": owner,
                    "run_id": item.get("run_id"),
                    "repo": item.get("repo"),
                    "language": item.get("language"),
                    "status": item.get("status"),
                    "duration_ms": int(item.get("duration_ms") or 0),
                    "findings_total": int(item.get("findings_total") or 0),
                }
            )
    if run_rows:
        try:
            client.table("validation_campaign_runs").insert(run_rows).execute()
        except Exception:
            logger.warning("Failed persisting validation_campaign_runs normalized rows.")

    profiles = _as_dict(payload.get("policy_profiles"))
    profile_rows: list[dict[str, Any]] = []
    for profile_id, raw in profiles.items():
        row = _as_dict(raw)
        profile_rows.append(
            {
                "profile_id": str(profile_id),
                "user_id": row.get("created_by"),
                "name": row.get("name"),
                "blocked_commands": _as_list(row.get("blocked_commands")),
                "restricted_paths": _as_list(row.get("restricted_paths")),
                "created_at": _parse_ts(row.get("created_at")),
                "updated_at": _parse_ts(row.get("created_at")),
            }
        )
    if profile_rows:
        try:
            client.table("program_policy_profiles").upsert(
                profile_rows,
                on_conflict="profile_id",
            ).execute()
        except Exception:
            logger.warning("Failed persisting program_policy_profiles normalized rows.")

    secrets = _as_dict(payload.get("secrets"))
    secret_rows: list[dict[str, Any]] = []
    for secret_id, raw in secrets.items():
        row = _as_dict(raw)
        encrypted = str(row.get("encrypted_value") or "")
        secret_rows.append(
            {
                "secret_id": str(secret_id),
                "user_id": row.get("created_by"),
                "name": row.get("name"),
                "encrypted_value": encrypted,
                "cipher_digest": sha256(encrypted.encode("utf-8")).hexdigest()[:16] if encrypted else "",
                "created_at": _parse_ts(row.get("created_at")),
                "updated_at": _parse_ts(row.get("created_at")),
            }
        )
    if secret_rows:
        try:
            client.table("program_secrets").upsert(
                secret_rows,
                on_conflict="secret_id",
            ).execute()
        except Exception:
            logger.warning("Failed persisting program_secrets normalized rows.")

    checklists = _as_dict(payload.get("release_checklists"))
    checklist_rows: list[dict[str, Any]] = []
    for release_id, raw in checklists.items():
        row = _as_dict(raw)
        checklist_rows.append(
            {
                "release_id": release_id,
                "user_id": row.get("updated_by"),
                "security_review": bool(row.get("security_review")),
                "slo_dashboard": bool(row.get("slo_dashboard")),
                "rollback_tested": bool(row.get("rollback_tested")),
                "docs_complete": bool(row.get("docs_complete")),
                "runbooks_ready": bool(row.get("runbooks_ready")),
                "updated_at": _parse_ts(row.get("updated_at")),
            }
        )
    if checklist_rows:
        try:
            client.table("release_checklists").upsert(
                checklist_rows,
                on_conflict="release_id",
            ).execute()
        except Exception:
            logger.warning("Failed persisting release_checklists normalized rows.")

    rollback_drills = _as_dict(payload.get("rollback_drills"))
    rollback_rows: list[dict[str, Any]] = []
    for release_id, raw in rollback_drills.items():
        row = _as_dict(raw)
        rollback_rows.append(
            {
                "release_id": release_id,
                "user_id": row.get("updated_by"),
                "passed": bool(row.get("passed")),
                "duration_minutes": int(row.get("duration_minutes") or 0),
                "issues_found": _as_list(row.get("issues_found")),
                "updated_at": _parse_ts(row.get("updated_at")),
            }
        )
    if rollback_rows:
        try:
            client.table("rollback_drills").upsert(
                rollback_rows,
                on_conflict="release_id",
            ).execute()
        except Exception:
            logger.warning("Failed persisting rollback_drills normalized rows.")

    decisions = _as_dict(payload.get("go_live_decisions"))
    decision_rows: list[dict[str, Any]] = []
    for release_id, raw in decisions.items():
        row = _as_dict(raw)
        decision_rows.append(
            {
                "release_id": release_id,
                "user_id": row.get("decided_by"),
                "status": row.get("status"),
                "reasons": _as_list(row.get("reasons")),
                "decided_at": _parse_ts(row.get("decided_at")),
            }
        )
    if decision_rows:
        try:
            client.table("go_live_decisions").upsert(
                decision_rows,
                on_conflict="release_id",
            ).execute()
        except Exception:
            logger.warning("Failed persisting go_live_decisions normalized rows.")

    idempotent = _as_dict(payload.get("idempotent_checkpoints"))
    idem_rows: list[dict[str, Any]] = []
    for joined_key, raw in idempotent.items():
        if not isinstance(joined_key, str) or "::" not in joined_key:
            continue
        build_id, idem_key = joined_key.split("::", 1)
        if not idem_key:
            continue
        row = _as_dict(raw)
        checkpoint = _as_dict(row.get("checkpoint"))
        idem_rows.append(
            {
                "build_id": build_id,
                "idempotency_key": idem_key,
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "status": checkpoint.get("status"),
                "reason": checkpoint.get("reason"),
                "created_ts": int(row.get("created_ts") or 0),
                "user_id": row.get("user_id") or "system",
                "created_at": _parse_ts(checkpoint.get("created_at")),
            }
        )
    if idem_rows:
        try:
            client.table("program_idempotent_checkpoints").upsert(
                idem_rows,
                on_conflict="build_id,idempotency_key",
            ).execute()
        except Exception:
            logger.warning("Failed persisting program_idempotent_checkpoints normalized rows.")

    return True
