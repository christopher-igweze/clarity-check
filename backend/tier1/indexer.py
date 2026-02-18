"""Deterministic Tier 1 repository indexing with commit-aware caching."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from config import settings
from services import supabase_client as db

logger = logging.getLogger(__name__)


SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("sk_live", re.compile(r"sk_live_[A-Za-z0-9]+")),
    ("sk_test", re.compile(r"sk_test_[A-Za-z0-9]+")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack_bot", re.compile(r"xoxb-[0-9A-Za-z-]+")),
    ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
]

ROUTE_PATTERNS = [
    re.compile(r"\bapp\.(get|post|put|delete|patch)\s*\("),
    re.compile(r"\brouter\.(get|post|put|delete|patch)\s*\("),
    re.compile(r"@(?:app|router)\.(get|post|put|delete|patch)\b"),
]

AUTH_HINT_PATTERN = re.compile(r"\b(auth|authenticate|authorization|jwt|clerk|session|current_user|require_auth)\b", re.IGNORECASE)
RATE_HINT_PATTERN = re.compile(r"\b(rate.?limit|throttle|slowapi|limiter|bucket)\b", re.IGNORECASE)

DANGEROUS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("eval", re.compile(r"\beval\s*\(")),
    ("new_function", re.compile(r"\bnew\s+Function\s*\(")),
    ("child_process_exec", re.compile(r"child_process\.(exec|execSync|spawnSync)\s*\(")),
    ("python_exec", re.compile(r"\b(exec|execfile)\s*\(")),
    ("pickle_loads", re.compile(r"pickle\.loads\s*\(")),
]

SQL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "sql_concat",
        re.compile(
            r"(SELECT|INSERT|UPDATE|DELETE)[^\n]{0,120}(\+|%s|f\"|f'|\.format\()",
            re.IGNORECASE,
        ),
    ),
    ("raw_query", re.compile(r"\b(query|execute)\s*\(\s*f?[\"']", re.IGNORECASE)),
]

ENV_USAGE_PATTERN = re.compile(r"(process\.env\.[A-Z0-9_]+|os\.getenv\(|os\.environ\[|import\.meta\.env\.)")

WEAK_ERROR_LOGGING_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bare_except", re.compile(r"^\s*except\s*:\s*$")),
    ("print_in_except", re.compile(r"except\s+Exception[^\n]*:\s*\n\s*print\(", re.IGNORECASE)),
    ("console_log_error", re.compile(r"console\.log\(.*(error|exception)", re.IGNORECASE)),
]

SYNC_BLOCKING_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("fs_sync", re.compile(r"\bfs\.[A-Za-z]+Sync\s*\(")),
    ("sync_subprocess", re.compile(r"subprocess\.(run|call|check_output)\s*\(")),
    ("requests_blocking", re.compile(r"\brequests\.(get|post|put|delete)\s*\(")),
]


class DeterministicIndexer:
    """Builds and caches deterministic Tier 1 index payloads."""

    async def build_or_reuse(
        self,
        *,
        project_id: UUID | None,
        user_id: str | None,
        repo_url: str,
        clone_url: str,
        repo_sha: str,
        github_token: str | None,
        scan_id: UUID | None = None,
    ) -> dict:
        if project_id is not None:
            cached = await db.get_project_index(project_id, repo_sha)
            if cached:
                index_json = cached.get("index_json") or {}
                return {
                    "repo_sha": repo_sha,
                    "loc_total": int(cached.get("loc_total") or 0),
                    "file_count": int(cached.get("file_count") or 0),
                    "index_json": index_json,
                    "cache_hit": True,
                    "metrics": {
                        "files_seen": int(cached.get("file_count") or 0),
                        "loc_total": int(cached.get("loc_total") or 0),
                        "cache_hit": True,
                    },
                }

        result = await asyncio.to_thread(
            self._build_index_sync,
            repo_url,
            clone_url,
            repo_sha,
            github_token,
            scan_id,
        )

        if project_id is not None and user_id is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=settings.tier1_index_ttl_days)
            await db.upsert_project_index(
                project_id=project_id,
                user_id=user_id,
                repo_sha=repo_sha,
                loc_total=result["loc_total"],
                file_count=result["file_count"],
                index_json=result["index_json"],
                expires_at=expires_at,
            )

        result["cache_hit"] = False
        result["metrics"] = {
            "files_seen": result["file_count"],
            "loc_total": result["loc_total"],
            "cache_hit": False,
        }
        return result

    def _build_index_sync(
        self,
        repo_url: str,
        clone_url: str,
        repo_sha: str,
        github_token: str | None,
        scan_id: UUID | None,
    ) -> dict:
        workspace_root = Path("/tmp") / "clarity-check" / "tier1" / str(scan_id or uuid4())
        repo_dir = workspace_root / "repo"

        shutil.rmtree(workspace_root, ignore_errors=True)
        workspace_root.mkdir(parents=True, exist_ok=True)

        clone_target = _clone_url_with_token(clone_url, github_token)

        try:
            _run(["git", "clone", "--depth", "1", clone_target, str(repo_dir)], timeout=120)
            # Ensure requested commit is checked out.
            _run(["git", "fetch", "--depth", "1", "origin", repo_sha], cwd=repo_dir, timeout=120)
            _run(["git", "checkout", repo_sha], cwd=repo_dir, timeout=30)
            # Best-effort additional history so git metadata signals are available.
            subprocess.run(
                ["git", "fetch", "--depth", "200", "origin"],
                cwd=str(repo_dir),
                text=True,
                capture_output=True,
                timeout=60,
                check=False,
            )

            files = _git_ls_files(repo_dir)
            indexed_files: list[dict] = []
            loc_total = 0

            signals: dict[str, list[dict]] = {
                "secret_matches": [],
                "private_key_matches": [],
                "insecure_cors_matches": [],
                "dangerous_exec_matches": [],
                "sql_matches": [],
                "route_hints": [],
                "env_usage": [],
                "weak_error_logging": [],
                "blocking_sync": [],
            }

            has_ci = False
            has_tests = False
            has_env_example = False
            tracked_env_files: list[str] = []
            manifests_present: set[str] = set()
            lockfiles_present: set[str] = set()

            for rel_path in files:
                # basic path-driven checks
                lower = rel_path.lower()
                if lower.startswith(".github/workflows/"):
                    has_ci = True
                if _is_test_path(lower):
                    has_tests = True
                if lower in {".env.example", ".env.sample", ".env.template"}:
                    has_env_example = True
                if _is_secret_env_file(lower):
                    tracked_env_files.append(rel_path)
                if _is_manifest_file(lower):
                    manifests_present.add(Path(rel_path).name)
                if _is_lockfile(lower):
                    lockfiles_present.add(Path(rel_path).name)

                abs_path = repo_dir / rel_path
                if not abs_path.exists() or not abs_path.is_file():
                    continue

                data = _read_text(abs_path)
                if data is None:
                    continue

                loc = _loc_count(data)
                loc_total += loc

                ext = abs_path.suffix.lower()
                sha256 = hashlib.sha256(data.encode("utf-8", errors="ignore")).hexdigest()

                indexed_files.append(
                    {
                        "path": rel_path,
                        "ext": ext,
                        "loc": loc,
                        "sha256": sha256,
                        "path_role": _path_role(lower),
                    }
                )

                # deterministic signal extraction
                _collect_secret_signals(rel_path, data, signals)
                _collect_cors_signals(rel_path, data, signals)
                _collect_dangerous_exec_signals(rel_path, data, signals)
                _collect_sql_signals(rel_path, data, signals)
                _collect_route_signals(rel_path, data, signals)
                _collect_env_signals(rel_path, data, signals)
                _collect_error_logging_signals(rel_path, data, signals)
                _collect_sync_blocking_signals(rel_path, data, signals)

            linter_probes = _run_linter_probes(repo_dir)

            index_json = {
                "repo_url": repo_url,
                "repo_sha": repo_sha,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "files": indexed_files,
                "signals": signals,
                "facts": {
                    "has_ci": has_ci,
                    "has_tests": has_tests,
                    "has_env_example": has_env_example,
                    "tracked_env_files": tracked_env_files,
                    "manifests_present": sorted(manifests_present),
                    "lockfiles_present": sorted(lockfiles_present),
                    "git_metadata": _collect_git_metadata(repo_dir),
                },
                "linter_probes": linter_probes,
            }

            return {
                "repo_sha": repo_sha,
                "loc_total": loc_total,
                "file_count": len(indexed_files),
                "index_json": index_json,
            }
        finally:
            shutil.rmtree(workspace_root, ignore_errors=True)


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def _git_ls_files(repo_dir: Path) -> list[str]:
    result = _run(["git", "ls-files"], cwd=repo_dir, timeout=30)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _clone_url_with_token(clone_url: str, token: str | None) -> str:
    if not token:
        return clone_url
    if clone_url.startswith("https://"):
        return clone_url.replace("https://", f"https://x-access-token:{token}@", 1)
    return clone_url


def _read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except Exception:
        return None
    if b"\x00" in raw:
        return None
    # cap huge files to keep indexing bounded
    if len(raw) > 1_500_000:
        raw = raw[:1_500_000]
    return raw.decode("utf-8", errors="replace")


def _loc_count(content: str) -> int:
    return sum(1 for line in content.splitlines() if line.strip())


def _is_test_path(lower_path: str) -> bool:
    return (
        "/test" in lower_path
        or "/tests" in lower_path
        or "__tests__" in lower_path
        or lower_path.endswith(".spec.ts")
        or lower_path.endswith(".spec.tsx")
        or lower_path.endswith(".spec.js")
        or lower_path.endswith(".spec.jsx")
        or lower_path.endswith("_test.py")
        or lower_path.endswith("test_.py")
    )


def _is_secret_env_file(lower_path: str) -> bool:
    name = Path(lower_path).name
    if not name.startswith(".env"):
        return False
    if name in {".env.example", ".env.sample", ".env.template"}:
        return False
    return True


def _is_manifest_file(lower_path: str) -> bool:
    return Path(lower_path).name in {
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "pom.xml",
        "go.mod",
        "cargo.toml",
    }


def _is_lockfile(lower_path: str) -> bool:
    return Path(lower_path).name in {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        "poetry.lock",
        "pipfile.lock",
        "cargo.lock",
    }


def _path_role(lower_path: str) -> str:
    if lower_path.startswith(".github/workflows/"):
        return "ci"
    if _is_test_path(lower_path):
        return "test"
    if lower_path.startswith("backend/") or "/api/" in lower_path or "/server/" in lower_path:
        return "backend"
    if lower_path.startswith("src/") or "/components/" in lower_path:
        return "frontend"
    if "/config" in lower_path or lower_path.endswith(('.yml', '.yaml', '.toml', '.ini', '.json')):
        return "config"
    return "source"


def _line_iter(content: str):
    for idx, line in enumerate(content.splitlines(), start=1):
        yield idx, line


def _add_signal(bucket: list[dict], file_path: str, line_number: int, snippet: str, match: str) -> None:
    bucket.append(
        {
            "file_path": file_path,
            "line_number": line_number,
            "snippet": snippet.strip()[:240],
            "match": match[:120],
        }
    )


def _collect_secret_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    for line_no, line in _line_iter(content):
        for name, pattern in SECRET_PATTERNS:
            m = pattern.search(line)
            if m:
                _add_signal(signals["secret_matches"], file_path, line_no, line, name)
        if "BEGIN PRIVATE KEY" in line or "BEGIN RSA PRIVATE KEY" in line:
            _add_signal(signals["private_key_matches"], file_path, line_no, line, "private_key")


def _collect_cors_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    lower = content.lower()
    has_wildcard = "allow_origins=['*'" in lower or 'allow_origins=["*"' in lower or "origin: '*'" in lower
    has_credentials = "allow_credentials=true" in lower or "credentials: true" in lower
    if has_wildcard and has_credentials:
        _add_signal(
            signals["insecure_cors_matches"],
            file_path,
            1,
            "Wildcard origin with credentials appears enabled.",
            "cors_wildcard_with_credentials",
        )


def _collect_dangerous_exec_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    for line_no, line in _line_iter(content):
        for name, pattern in DANGEROUS_PATTERNS:
            if pattern.search(line):
                _add_signal(signals["dangerous_exec_matches"], file_path, line_no, line, name)


def _collect_sql_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    for line_no, line in _line_iter(content):
        for name, pattern in SQL_PATTERNS:
            if pattern.search(line):
                _add_signal(signals["sql_matches"], file_path, line_no, line, name)


def _collect_route_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        if not any(p.search(line) for p in ROUTE_PATTERNS):
            continue

        window = "\n".join(lines[max(0, idx - 5) : min(len(lines), idx + 15)])
        has_auth = bool(AUTH_HINT_PATTERN.search(window))
        has_rate_limit = bool(RATE_HINT_PATTERN.search(window))
        signals["route_hints"].append(
            {
                "file_path": file_path,
                "line_number": idx,
                "snippet": line.strip()[:240],
                "has_auth": has_auth,
                "has_rate_limit": has_rate_limit,
            }
        )


def _collect_env_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    for line_no, line in _line_iter(content):
        m = ENV_USAGE_PATTERN.search(line)
        if m:
            _add_signal(signals["env_usage"], file_path, line_no, line, m.group(1))


def _collect_error_logging_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    for line_no, line in _line_iter(content):
        for name, pattern in WEAK_ERROR_LOGGING_PATTERNS:
            if pattern.search(line):
                _add_signal(signals["weak_error_logging"], file_path, line_no, line, name)


def _collect_sync_blocking_signals(file_path: str, content: str, signals: dict[str, list[dict]]) -> None:
    for line_no, line in _line_iter(content):
        for name, pattern in SYNC_BLOCKING_PATTERNS:
            if pattern.search(line):
                _add_signal(signals["blocking_sync"], file_path, line_no, line, name)


def _run_linter_probes(repo_dir: Path) -> list[dict]:
    probes: list[dict] = []
    commands = {
        "ruff": ["ruff", "check", ".", "--output-format", "json"],
        "eslint": ["eslint", ".", "-f", "json"],
        "bandit": ["bandit", "-r", ".", "-f", "json"],
        "semgrep": ["semgrep", "--config", "auto", "--json", "."],
    }

    for tool_name, cmd in commands.items():
        if shutil.which(tool_name) is None:
            continue
        try:
            result = subprocess.run(
                cmd,
                cwd=str(repo_dir),
                text=True,
                capture_output=True,
                timeout=20,
                check=False,
            )
            probes.append(
                {
                    "tool": tool_name,
                    "exit_code": int(result.returncode),
                    "stdout": (result.stdout or "")[:40_000],
                    "stderr": (result.stderr or "")[:4_000],
                }
            )
        except Exception as exc:
            probes.append({"tool": tool_name, "error": str(exc)})

    return probes


def _collect_git_metadata(repo_dir: Path) -> dict:
    """Collect lightweight git history metadata for report context."""
    metadata = {
        "history_available": False,
        "commit_count_90d": 0,
        "contributors_90d": 0,
        "top_churn_files_90d": [],
        "latest_commit_at": None,
    }
    try:
        latest = subprocess.run(
            ["git", "log", "-1", "--format=%cI"],
            cwd=str(repo_dir),
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        latest_commit_at = (latest.stdout or "").strip()
        if latest_commit_at:
            metadata["latest_commit_at"] = latest_commit_at

        commit_count = subprocess.run(
            ["git", "rev-list", "--count", "--since=90.days", "HEAD"],
            cwd=str(repo_dir),
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        count_raw = (commit_count.stdout or "").strip()
        commit_total = int(count_raw) if count_raw.isdigit() else 0
        metadata["commit_count_90d"] = commit_total

        contributors = subprocess.run(
            ["git", "log", "--since=90.days", "--format=%an"],
            cwd=str(repo_dir),
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        names = {
            line.strip()
            for line in (contributors.stdout or "").splitlines()
            if line.strip()
        }
        metadata["contributors_90d"] = len(names)

        churn = subprocess.run(
            ["git", "log", "--since=90.days", "--name-only", "--pretty=format:"],
            cwd=str(repo_dir),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        counts: dict[str, int] = {}
        for line in (churn.stdout or "").splitlines():
            path = line.strip()
            if not path:
                continue
            counts[path] = counts.get(path, 0) + 1

        top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10]
        metadata["top_churn_files_90d"] = [
            {"file_path": path, "touch_count": touches}
            for path, touches in top
        ]

        metadata["history_available"] = bool(
            metadata["latest_commit_at"]
            or metadata["commit_count_90d"]
            or metadata["top_churn_files_90d"]
        )
    except Exception:
        # Best-effort only; scanner/report should keep running without git history.
        return metadata

    return metadata
