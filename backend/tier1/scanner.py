"""Tier 1 deterministic scanner (Balanced 15 checks)."""

from __future__ import annotations

from typing import Any

from tier1.contracts import Tier1Evidence, Tier1Finding

LOCKFILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "poetry.lock",
    "pipfile.lock",
    "cargo.lock",
}


def _evidence_from_rows(rows: list[dict], limit: int = 5) -> list[Tier1Evidence]:
    items: list[Tier1Evidence] = []
    for row in rows[:limit]:
        items.append(
            Tier1Evidence(
                file_path=str(row.get("file_path") or "unknown"),
                line_number=row.get("line_number"),
                snippet=str(row.get("snippet") or "")[:220],
                match=str(row.get("match") or "")[:120],
            )
        )
    return items


class DeterministicScanner:
    """Runs the locked Tier 1 deterministic check set."""

    def scan(self, *, index_payload: dict, sensitive_data: list[str] | None = None) -> list[Tier1Finding]:
        index_json = index_payload.get("index_json") or {}
        signals = index_json.get("signals") or {}
        facts = index_json.get("facts") or {}
        files = index_json.get("files") or []

        findings: list[Tier1Finding] = []

        secret_matches = list(signals.get("secret_matches") or [])
        findings.append(
            self._build_check(
                check_id="SEC_001",
                title="Hardcoded API keys/secrets",
                description="Detected token/key patterns committed in tracked source files.",
                category="security",
                severity="critical",
                engine="regex",
                status="fail" if secret_matches else "pass",
                confidence=0.98 if secret_matches else 1.0,
                evidence=_evidence_from_rows(secret_matches),
                suggested_fix_stub="Move secrets to environment variables, rotate exposed keys, and remove committed values from git history.",
            )
        )

        private_keys = list(signals.get("private_key_matches") or [])
        findings.append(
            self._build_check(
                check_id="SEC_002",
                title="Private key material committed",
                description="Detected private key markers in tracked files.",
                category="security",
                severity="critical",
                engine="regex",
                status="fail" if private_keys else "pass",
                confidence=0.99 if private_keys else 1.0,
                evidence=_evidence_from_rows(private_keys),
                suggested_fix_stub="Remove private key material from repository, rotate credentials, and load keys from secure secret storage.",
            )
        )

        tracked_env_files = list(facts.get("tracked_env_files") or [])
        env_file_evidence = [
            {"file_path": p, "line_number": None, "snippet": p, "match": "tracked_env_file"}
            for p in tracked_env_files
        ]
        findings.append(
            self._build_check(
                check_id="SEC_003",
                title="Secret-bearing env files committed",
                description="Tracked .env files increase secret leak risk in source control.",
                category="security",
                severity="high",
                engine="index",
                status="fail" if tracked_env_files else "pass",
                confidence=0.95 if tracked_env_files else 1.0,
                evidence=_evidence_from_rows(env_file_evidence),
                suggested_fix_stub="Keep only template env files (.env.example) in git and ignore real env files with .gitignore.",
            )
        )

        insecure_cors = list(signals.get("insecure_cors_matches") or [])
        findings.append(
            self._build_check(
                check_id="SEC_004",
                title="Insecure CORS configuration",
                description="Detected wildcard origins together with credentialed requests.",
                category="security",
                severity="high",
                engine="ast",
                status="fail" if insecure_cors else "pass",
                confidence=0.85 if insecure_cors else 1.0,
                evidence=_evidence_from_rows(insecure_cors),
                suggested_fix_stub="Restrict allowed origins to explicit trusted domains and avoid allow_credentials with wildcard origins.",
            )
        )

        dangerous_exec = list(signals.get("dangerous_exec_matches") or [])
        findings.append(
            self._build_check(
                check_id="SEC_005",
                title="Dangerous dynamic execution patterns",
                description="Detected dynamic execution calls that can execute untrusted input.",
                category="security",
                severity="high",
                engine="ast",
                status="fail" if dangerous_exec else "pass",
                confidence=0.85 if dangerous_exec else 1.0,
                evidence=_evidence_from_rows(dangerous_exec),
                suggested_fix_stub="Replace eval/dynamic execution with strict allowlisted dispatch and validated inputs.",
            )
        )

        sql_matches = list(signals.get("sql_matches") or [])
        findings.append(
            self._build_check(
                check_id="SEC_006",
                title="SQL injection-risk query construction",
                description="Detected SQL construction patterns that appear to use interpolation or concatenation.",
                category="security",
                severity="high",
                engine="ast",
                status="fail" if len(sql_matches) >= 2 else ("warn" if sql_matches else "pass"),
                confidence=0.8 if sql_matches else 1.0,
                evidence=_evidence_from_rows(sql_matches),
                suggested_fix_stub="Use parameterized queries/placeholders for all user-controlled inputs.",
            )
        )

        route_hints = list(signals.get("route_hints") or [])
        unauth_routes = [row for row in route_hints if not row.get("has_auth")]
        findings.append(
            self._build_check(
                check_id="SEC_007",
                title="Missing auth guard hints on API routes",
                description="Detected route handlers without nearby auth middleware/guard indicators.",
                category="security",
                severity="medium",
                engine="ast",
                status="warn" if unauth_routes else "pass",
                confidence=0.7 if unauth_routes else 1.0,
                evidence=_evidence_from_rows(unauth_routes),
                suggested_fix_stub="Attach explicit authentication/authorization middleware to exposed routes.",
            )
        )

        has_tests = bool(facts.get("has_tests"))
        findings.append(
            self._build_check(
                check_id="REL_001",
                title="Missing automated tests",
                description="No test directories/files were detected from tracked source paths.",
                category="reliability",
                severity="high",
                engine="index",
                status="fail" if not has_tests else "pass",
                confidence=0.9,
                evidence=[] if has_tests else [Tier1Evidence(file_path="(repo)", snippet="No tests matched known test patterns", match="missing_tests")],
                suggested_fix_stub="Add baseline unit/integration tests for core user flows and CI-gated regression checks.",
            )
        )

        has_ci = bool(facts.get("has_ci"))
        findings.append(
            self._build_check(
                check_id="REL_002",
                title="Missing CI workflow",
                description="No .github/workflows pipeline was detected.",
                category="reliability",
                severity="medium",
                engine="index",
                status="warn" if not has_ci else "pass",
                confidence=0.95,
                evidence=[] if has_ci else [Tier1Evidence(file_path=".github/workflows", snippet="No workflow files found", match="missing_ci")],
                suggested_fix_stub="Add CI workflow to run lint, tests, and build checks on pull requests.",
            )
        )

        manifests_present = list(facts.get("manifests_present") or [])
        lockfiles_present = list(facts.get("lockfiles_present") or [])
        missing_lockfile = bool(manifests_present and not lockfiles_present)
        findings.append(
            self._build_check(
                check_id="REL_003",
                title="Missing lockfile for dependency reproducibility",
                description="Dependency manifests were found without a matching lockfile.",
                category="reliability",
                severity="medium",
                engine="index",
                status="warn" if missing_lockfile else "pass",
                confidence=0.9,
                evidence=[] if not missing_lockfile else [
                    Tier1Evidence(
                        file_path="(repo)",
                        snippet=f"Manifests: {', '.join(manifests_present)}",
                        match="missing_lockfile",
                    )
                ],
                suggested_fix_stub="Commit lockfiles for deterministic dependency installs in CI and production builds.",
            )
        )

        env_usage = list(signals.get("env_usage") or [])
        has_env_example = bool(facts.get("has_env_example"))
        missing_env_template = bool(env_usage and not has_env_example)
        findings.append(
            self._build_check(
                check_id="REL_004",
                title="Env vars used but no .env.example",
                description="Environment variables are referenced but no template env file was found.",
                category="reliability",
                severity="medium",
                engine="hybrid",
                status="warn" if missing_env_template else "pass",
                confidence=0.82 if missing_env_template else 1.0,
                evidence=_evidence_from_rows(env_usage) if missing_env_template else [],
                suggested_fix_stub="Add .env.example documenting required variables and safe default placeholders.",
            )
        )

        weak_error_logging = list(signals.get("weak_error_logging") or [])
        linter_probes = list(index_json.get("linter_probes") or [])
        linter_errors = [p for p in linter_probes if int(p.get("exit_code") or 0) != 0]
        rel5_rows: list[dict[str, Any]] = weak_error_logging[:]
        rel5_rows.extend(
            {
                "file_path": p.get("tool", "linter"),
                "line_number": None,
                "snippet": (p.get("stderr") or p.get("stdout") or "")[:180],
                "match": "linter_issue",
            }
            for p in linter_errors[:3]
        )
        findings.append(
            self._build_check(
                check_id="REL_005",
                title="Weak error/logging hygiene in backend paths",
                description="Detected weak exception/logging patterns and/or lint warnings in server code.",
                category="reliability",
                severity="low",
                engine="hybrid",
                status="warn" if rel5_rows else "pass",
                confidence=0.7 if rel5_rows else 1.0,
                evidence=_evidence_from_rows(rel5_rows),
                suggested_fix_stub="Use structured logger calls and explicit exception handling with actionable context.",
            )
        )

        source_candidates = [f for f in files if not _is_lockfile_path(str(f.get("path") or ""))]
        largest_files = sorted(source_candidates, key=lambda f: int(f.get("loc") or 0), reverse=True)[:3]
        over_500 = [f for f in source_candidates if int(f.get("loc") or 0) > 500]
        over_800 = [f for f in source_candidates if int(f.get("loc") or 0) > 800]
        status = "pass"
        severity = "medium"
        if over_800:
            status = "fail"
            severity = "high"
        elif over_500:
            status = "warn"
        findings.append(
            self._build_check(
                check_id="SCL_001",
                title="God file size threshold exceeded",
                description="Large hand-maintained source files may indicate high coupling and maintenance risk.",
                category="scalability",
                severity=severity,
                engine="index",
                status=status,
                confidence=0.95,
                evidence=[
                    Tier1Evidence(
                        file_path=str(f.get("path") or "unknown"),
                        line_number=None,
                        snippet=f"LOC={int(f.get('loc') or 0)}",
                        match="large_file",
                    )
                    for f in largest_files
                    if int(f.get("loc") or 0) > 500
                ],
                suggested_fix_stub="Break large modules into smaller domain-focused components and isolate shared utilities.",
            )
        )

        blocking_sync = list(signals.get("blocking_sync") or [])
        findings.append(
            self._build_check(
                check_id="SCL_002",
                title="Blocking sync operations in request paths",
                description="Detected synchronous/blocking calls that can increase latency under load.",
                category="scalability",
                severity="medium",
                engine="ast",
                status="warn" if blocking_sync else "pass",
                confidence=0.75 if blocking_sync else 1.0,
                evidence=_evidence_from_rows(blocking_sync),
                suggested_fix_stub="Prefer async/non-blocking IO for request handlers and move heavy work off the hot path.",
            )
        )

        no_rate_limit_routes = [row for row in route_hints if not row.get("has_rate_limit")]
        findings.append(
            self._build_check(
                check_id="SCL_003",
                title="Missing rate limiting hints on exposed APIs",
                description="Detected route handlers without nearby rate limiting indicators.",
                category="scalability",
                severity="medium",
                engine="ast",
                status="warn" if no_rate_limit_routes else "pass",
                confidence=0.7 if no_rate_limit_routes else 1.0,
                evidence=_evidence_from_rows(no_rate_limit_routes),
                suggested_fix_stub="Add route-level or global rate limiting to protect critical endpoints from abuse spikes.",
            )
        )

        self._apply_severity_escalation(findings, sensitive_data or [])
        return findings

    @staticmethod
    def _build_check(
        *,
        check_id: str,
        title: str,
        description: str,
        category: str,
        severity: str,
        engine: str,
        status: str,
        confidence: float,
        evidence: list[Tier1Evidence],
        suggested_fix_stub: str,
    ) -> Tier1Finding:
        return Tier1Finding(
            check_id=check_id,
            status=status,
            category=category,
            severity=severity,
            engine=engine,
            confidence=max(0.0, min(1.0, confidence)),
            title=title,
            description=description,
            evidence=evidence,
            suggested_fix_stub=suggested_fix_stub,
        )

    @staticmethod
    def _apply_severity_escalation(findings: list[Tier1Finding], sensitive_data: list[str]) -> None:
        sensitive_flag = any(item in {"payments", "pii", "health", "auth_secrets"} for item in sensitive_data)

        for finding in findings:
            if finding.status == "pass":
                continue

            should_escalate = False
            if len(finding.evidence) >= 3:
                should_escalate = True
            if sensitive_flag and finding.category == "security":
                should_escalate = True

            if should_escalate:
                finding.severity = _bump_severity(finding.severity)


def _bump_severity(severity: str) -> str:
    order = ["low", "medium", "high", "critical"]
    if severity not in order:
        return severity
    idx = order.index(severity)
    if idx >= len(order) - 1:
        return severity
    return order[idx + 1]


def _is_lockfile_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].lower()
    return name in LOCKFILE_NAMES
