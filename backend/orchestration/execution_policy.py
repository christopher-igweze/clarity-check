"""Per-node execution policy checks before runtime executor launch."""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from models.builds import BuildRun

_BLOCKED_COMMAND_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-f[dDxX]*\b", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
    re.compile(r"\bmkfs\.", re.IGNORECASE),
    re.compile(r"\bdd\s+if=.*\s+of=/dev/", re.IGNORECASE),
    re.compile(r"\bshutdown\b", re.IGNORECASE),
    re.compile(r"\breboot\b", re.IGNORECASE),
    re.compile(r"\bpoweroff\b", re.IGNORECASE),
)

_DEFAULT_BLOCKED_PATHS: tuple[str, ...] = (
    ".git",
    ".env",
    ".ssh",
    "/root",
    "/etc",
)

_CONTROL_TOKENS = {"&&", "||", "|", ";", "(", ")", "{", "}"}


@dataclass(frozen=True)
class NodePolicyResult:
    allowed: bool
    code: str | None = None
    message: str | None = None
    details: dict[str, Any] | None = None

    @classmethod
    def allow(cls) -> "NodePolicyResult":
        return cls(allowed=True, details={})

    @classmethod
    def deny(
        cls,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> "NodePolicyResult":
        return cls(
            allowed=False,
            code=code,
            message=message,
            details=details or {},
        )


def evaluate_node_execution_policy(
    *,
    build: BuildRun,
    node_id: str,
    runner_kind: str,
    command: str | None = None,
) -> NodePolicyResult:
    metadata = build.metadata if isinstance(build.metadata, dict) else {}
    node_policy = _resolve_node_policy(metadata, node_id=node_id)
    available_capabilities = _as_str_set(
        metadata.get("executor_capabilities")
        or metadata.get("capabilities")
    )
    required_capabilities = _required_capabilities(metadata, node_policy=node_policy, node_id=node_id)

    if required_capabilities and not _capabilities_satisfied(
        required=required_capabilities,
        available=available_capabilities,
    ):
        return NodePolicyResult.deny(
            code="missing_capability",
            message=f"Node '{node_id}' missing required execution capability.",
            details={
                "node_id": node_id,
                "runner_kind": runner_kind,
                "required_capabilities": sorted(required_capabilities),
                "available_capabilities": sorted(available_capabilities),
            },
        )

    effective_command = str(command or "").strip()
    if not effective_command:
        return NodePolicyResult.allow()

    for pattern in _BLOCKED_COMMAND_PATTERNS:
        if pattern.search(effective_command):
            return NodePolicyResult.deny(
                code="blocked_command",
                message="Command blocked by execution policy.",
                details={
                    "node_id": node_id,
                    "runner_kind": runner_kind,
                    "command_preview": effective_command[:300],
                },
            )

    lowered_command = effective_command.casefold()
    blocked_terms = _as_str_list(node_policy.get("blocked_commands")) + _as_str_list(
        metadata.get("policy_blocked_commands")
    )
    for term in blocked_terms:
        lowered_term = term.casefold()
        if lowered_term and lowered_term in lowered_command:
            return NodePolicyResult.deny(
                code="blocked_command",
                message="Command blocked by custom node policy.",
                details={
                    "node_id": node_id,
                    "runner_kind": runner_kind,
                    "blocked_term": term,
                    "command_preview": effective_command[:300],
                },
            )

    referenced_paths = _extract_paths_from_command(effective_command)
    if not referenced_paths:
        return NodePolicyResult.allow()

    workspace_root = str(metadata.get("workspace_root") or "/home/daytona/repo")
    blocked_paths = _resolve_roots(
        paths=_as_str_list(node_policy.get("blocked_paths"))
        + _as_str_list(metadata.get("policy_blocked_paths"))
        + list(_DEFAULT_BLOCKED_PATHS),
        workspace_root=workspace_root,
    )
    for raw_path in referenced_paths:
        path_abs = _to_abs_path(raw_path, workspace_root=workspace_root)
        if any(_is_same_or_child(path_abs, root) for root in blocked_paths):
            return NodePolicyResult.deny(
                code="blocked_path",
                message="Command references a blocked path.",
                details={
                    "node_id": node_id,
                    "runner_kind": runner_kind,
                    "path": raw_path,
                },
            )

    allowed_roots_raw = _as_str_list(node_policy.get("allowed_paths")) + _as_str_list(
        metadata.get("policy_allowed_paths")
    )
    if allowed_roots_raw:
        allowed_roots = _resolve_roots(paths=allowed_roots_raw, workspace_root=workspace_root)
        for raw_path in referenced_paths:
            path_abs = _to_abs_path(raw_path, workspace_root=workspace_root)
            if not any(_is_same_or_child(path_abs, root) for root in allowed_roots):
                return NodePolicyResult.deny(
                    code="path_outside_allowlist",
                    message="Command path is outside the node allowlist.",
                    details={
                        "node_id": node_id,
                        "runner_kind": runner_kind,
                        "path": raw_path,
                        "allowed_paths": allowed_roots_raw,
                    },
                )

    return NodePolicyResult.allow()


def _resolve_node_policy(metadata: dict[str, Any], *, node_id: str) -> dict[str, Any]:
    raw_policy = metadata.get("node_policy")
    if isinstance(raw_policy, dict):
        node_entry = raw_policy.get(node_id)
        if isinstance(node_entry, dict):
            return node_entry
    return {}


def _required_capabilities(
    metadata: dict[str, Any],
    *,
    node_policy: dict[str, Any],
    node_id: str,
) -> set[str]:
    required = set()
    required.update(_as_str_set(metadata.get("required_capabilities")))
    per_node = metadata.get("node_required_capabilities")
    if isinstance(per_node, dict):
        required.update(_as_str_set(per_node.get(node_id)))
    required.update(_as_str_set(node_policy.get("required_capabilities")))
    return required


def _capabilities_satisfied(*, required: set[str], available: set[str]) -> bool:
    if not required:
        return True
    if "*" in available:
        return True
    return required.issubset(available)


def _as_str_set(raw: object) -> set[str]:
    if raw is None:
        return set()
    if isinstance(raw, str):
        token = raw.strip()
        return {token} if token else set()
    if not isinstance(raw, list):
        return set()
    values: set[str] = set()
    for item in raw:
        token = str(item).strip()
        if token:
            values.add(token)
    return values


def _as_str_list(raw: object) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        token = raw.strip()
        return [token] if token else []
    if not isinstance(raw, list):
        return []
    values: list[str] = []
    for item in raw:
        token = str(item).strip()
        if token:
            values.append(token)
    return values


def _extract_paths_from_command(command: str) -> list[str]:
    try:
        tokens = shlex.split(command)
    except Exception:
        return []

    paths: list[str] = []
    for token in tokens:
        if token in _CONTROL_TOKENS:
            continue
        if token.startswith("-"):
            continue
        if "://" in token:
            continue
        if token in {".", ".."}:
            paths.append(token)
            continue
        if token.startswith("/") or token.startswith("./") or token.startswith("../"):
            paths.append(token)
            continue
        if "/" in token:
            paths.append(token)
    return paths


def _resolve_roots(*, paths: list[str], workspace_root: str) -> list[str]:
    roots: list[str] = []
    for raw in paths:
        candidate = _to_abs_path(raw, workspace_root=workspace_root)
        if candidate not in roots:
            roots.append(candidate)
    return roots


def _to_abs_path(path: str, *, workspace_root: str) -> str:
    normalized = path.strip()
    if not normalized:
        return str(PurePosixPath(workspace_root))
    if normalized in {".", "./"}:
        return str(PurePosixPath(workspace_root))
    if normalized.startswith("/"):
        return str(PurePosixPath(normalized))
    while normalized.startswith("./"):
        normalized = normalized[2:]
    joined = PurePosixPath(workspace_root) / normalized
    return str(joined)


def _is_same_or_child(path: str, root: str) -> bool:
    path_obj = PurePosixPath(path)
    root_obj = PurePosixPath(root)
    return path_obj == root_obj or root_obj in path_obj.parents
