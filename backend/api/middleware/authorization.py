"""Capability-based authorization helpers for control-plane routes."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import HTTPException, Request

from config import settings

ROLE_CAPABILITIES: dict[str, set[str]] = {
    "viewer": {
        "program.validation.read",
        "program.policy.read",
        "program.secrets.read",
        "program.runtime.read",
        "program.release.read",
    },
    "operator": {
        "program.validation.read",
        "program.validation.write",
        "program.policy.read",
        "program.policy.write",
        "program.policy.check",
        "program.runtime.read",
        "program.runtime.write",
        "program.release.read",
        "program.release.write",
    },
    "security": {
        "program.validation.read",
        "program.policy.read",
        "program.policy.write",
        "program.policy.check",
        "program.secrets.read",
        "program.secrets.write",
        "program.webhook.ingest",
        "program.runtime.read",
    },
    "admin": {"*"},
}


def _to_str_set(raw: object) -> set[str]:
    if raw is None:
        return set()
    if isinstance(raw, str):
        value = raw.strip()
        return {value} if value else set()
    if isinstance(raw, Iterable):
        values: set[str] = set()
        for item in raw:
            if isinstance(item, str):
                token = item.strip()
                if token:
                    values.add(token)
        return values
    return set()


def derive_roles_and_capabilities(payload: dict) -> tuple[list[str], list[str]]:
    roles = set()
    capabilities = set()

    roles.update(_to_str_set(payload.get("role")))
    roles.update(_to_str_set(payload.get("roles")))
    roles.update(_to_str_set(payload.get("org_role")))
    roles.update(_to_str_set(payload.get("org_roles")))
    app_meta = payload.get("app_metadata")
    user_meta = payload.get("user_metadata")
    if isinstance(app_meta, dict):
        roles.update(_to_str_set(app_meta.get("role")))
        roles.update(_to_str_set(app_meta.get("roles")))
    if isinstance(user_meta, dict):
        roles.update(_to_str_set(user_meta.get("role")))
        roles.update(_to_str_set(user_meta.get("roles")))

    capabilities.update(_to_str_set(payload.get("capabilities")))
    capabilities.update(_to_str_set(payload.get("permissions")))
    capabilities.update(_to_str_set(payload.get("org_permissions")))
    if isinstance(app_meta, dict):
        capabilities.update(_to_str_set(app_meta.get("capabilities")))
        capabilities.update(_to_str_set(app_meta.get("permissions")))
    if isinstance(user_meta, dict):
        capabilities.update(_to_str_set(user_meta.get("capabilities")))
        capabilities.update(_to_str_set(user_meta.get("permissions")))

    normalized_roles = {role.strip().lower() for role in roles if role.strip()}
    for role in normalized_roles:
        capabilities.update(ROLE_CAPABILITIES.get(role, set()))

    return sorted(normalized_roles), sorted(capabilities)


def require_capability(request: Request, capability: str) -> None:
    if not settings.enforce_capability_auth:
        return
    raw = getattr(request.state, "capabilities", None)
    if not raw:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "capabilities_missing",
                "message": "Capability set missing for this request.",
            },
        )
    if isinstance(raw, str):
        capabilities = {raw}
    else:
        capabilities = {str(item) for item in raw}
    if "*" in capabilities or capability in capabilities:
        return
    raise HTTPException(
        status_code=403,
        detail={
            "code": "insufficient_capability",
            "message": f"Missing required capability: {capability}",
        },
    )
