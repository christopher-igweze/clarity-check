"""Tier 1 orchestration: deterministic index -> deterministic scan -> assistant report."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID

from models.agent_log import AgentLogEntry, AgentName, LogLevel, SSEEventType
from models.findings import AuditReport, Category, Finding, FindingSource, Severity
from models.scan import PrimerResult
from services.github import get_head_sha, get_repo_info, parse_repo_url
from tier1.indexer import DeterministicIndexer
from tier1.reporter import Tier1Reporter
from tier1.scanner import DeterministicScanner

logger = logging.getLogger(__name__)


class Tier1Orchestrator:
    def __init__(
        self,
        *,
        scan_id: UUID,
        repo_url: str,
        project_id: UUID,
        user_id: str,
        project_intake: dict,
        primer: PrimerResult | None,
        emit: Callable[[AgentLogEntry], Any],
        github_token: str | None,
        user_preferences: dict | None = None,
        run_context: dict | None = None,
    ) -> None:
        self.scan_id = scan_id
        self.repo_url = repo_url
        self.project_id = project_id
        self.user_id = user_id
        self.project_intake = project_intake
        self.primer = primer
        self.emit = emit
        self.github_token = github_token
        self.user_preferences = user_preferences
        self.run_context = run_context or {}

        self.indexer = DeterministicIndexer()
        self.scanner = DeterministicScanner()
        self.reporter = Tier1Reporter()

    def _log(
        self,
        *,
        event_type: SSEEventType,
        agent: AgentName,
        message: str,
        level: LogLevel = LogLevel.info,
        data: dict | None = None,
    ) -> None:
        self.emit(
            AgentLogEntry(
                event_type=event_type,
                agent=agent,
                message=message,
                level=level,
                data=data,
            )
        )

    async def run(self) -> dict:
        run_started_perf = time.perf_counter()
        run_started_at = datetime.now(timezone.utc).isoformat()

        owner, repo = await parse_repo_url(self.repo_url)
        repo_info = await get_repo_info(owner, repo, self.github_token)
        repo_sha = await get_head_sha(
            owner,
            repo,
            repo_info.default_branch,
            self.github_token,
        )

        self._log(
            event_type=SSEEventType.agent_start,
            agent=AgentName.scanner,
            message="Deterministic indexing and scan started.",
            data={"repo_sha": repo_sha},
        )

        index_started_perf = time.perf_counter()
        index_payload = await self.indexer.build_or_reuse(
            project_id=self.project_id,
            user_id=self.user_id,
            repo_url=self.repo_url,
            clone_url=repo_info.clone_url,
            repo_sha=repo_sha,
            github_token=self.github_token,
            scan_id=self.scan_id,
        )
        index_ms = int((time.perf_counter() - index_started_perf) * 1000)

        scan_started_perf = time.perf_counter()
        findings = self.scanner.scan(
            index_payload=index_payload,
            sensitive_data=list(self.project_intake.get("sensitive_data") or []),
        )
        scan_ms = int((time.perf_counter() - scan_started_perf) * 1000)

        actionable = [f for f in findings if f.status in {"warn", "fail"}]
        score_summary = self._score(findings)
        index_json = index_payload.get("index_json") or {}
        index_facts = index_json.get("facts") or {}
        git_metadata = index_facts.get("git_metadata") or {}
        cache_hit = bool(index_payload.get("cache_hit"))

        run_details = {
            "scan_id": str(self.scan_id),
            "repo_sha": repo_sha,
            "run_started_at": run_started_at,
            "index_source": "cache" if cache_hit else "fresh",
            "cache_hit": cache_hit,
            "file_count": int(index_payload.get("file_count") or 0),
            "loc_total": int(index_payload.get("loc_total") or 0),
            "index_generated_at": index_json.get("generated_at"),
            "index_ms": index_ms,
            "scan_ms": scan_ms,
            "checks_evaluated": len(findings),
            "total_before_report_ms": int((time.perf_counter() - run_started_perf) * 1000),
            "reports_generated_before": self.run_context.get("reports_generated_before"),
            "report_limit": self.run_context.get("report_limit"),
        }

        self._log(
            event_type=SSEEventType.agent_complete,
            agent=AgentName.scanner,
            message=f"Deterministic scan complete with {len(actionable)} actionable findings.",
            level=LogLevel.success,
            data={
                "findings_count": len(actionable),
                "files_seen": index_payload.get("file_count", 0),
                "loc_total": index_payload.get("loc_total", 0),
                "cache_hit": bool(index_payload.get("cache_hit")),
            },
        )

        self._log(
            event_type=SSEEventType.agent_start,
            agent=AgentName.educator,
            message="Generating Tier 1 assistant report.",
        )

        artifact = await self.reporter.generate_report(
            findings=findings,
            score_summary=score_summary,
            intake_context=self.project_intake,
            user_preferences=self.user_preferences,
            run_details=run_details,
            git_metadata=git_metadata,
            index_facts=index_facts,
        )

        audit_report = self._to_audit_report(
            findings=findings,
            score_summary=score_summary,
        )

        return {
            "repo_sha": repo_sha,
            "findings": findings,
            "actionable_findings": actionable,
            "scores": score_summary,
            "loc_total": index_payload.get("loc_total", 0),
            "file_count": index_payload.get("file_count", 0),
            "cache_hit": cache_hit,
            "index_facts": index_facts,
            "git_metadata": git_metadata,
            "run_details": (artifact.summary_json.get("run_details") or {}),
            "artifact": artifact,
            "audit_report": audit_report,
        }

    @staticmethod
    def _score(findings: list) -> dict:
        penalties = {
            "critical": 18,
            "high": 10,
            "medium": 6,
            "low": 3,
        }

        scores = {
            "security": 100,
            "reliability": 100,
            "scalability": 100,
        }

        for finding in findings:
            if finding.status == "pass":
                continue
            penalty = penalties.get(finding.severity, 4)
            if finding.status == "warn":
                penalty = max(1, penalty // 2)
            category = finding.category
            scores[category] = max(0, scores.get(category, 100) - penalty)

        health_score = round((scores["security"] + scores["reliability"] + scores["scalability"]) / 3)

        return {
            "health_score": int(health_score),
            "security_score": int(scores["security"]),
            "reliability_score": int(scores["reliability"]),
            "scalability_score": int(scores["scalability"]),
        }

    def _to_audit_report(self, *, findings: list, score_summary: dict) -> AuditReport:
        converted: list[Finding] = []

        for finding in findings:
            if finding.status == "pass":
                continue

            evidence = finding.evidence[0] if finding.evidence else None
            description = finding.description
            if finding.suggested_fix_stub:
                description = f"{description}\n\nSuggested fix: {finding.suggested_fix_stub}"

            converted.append(
                Finding(
                    title=f"{finding.check_id}: {finding.title}",
                    description=description,
                    category=Category(finding.category),
                    severity=Severity(finding.severity),
                    source=FindingSource.static,
                    file_path=evidence.file_path if evidence else None,
                    line_number=evidence.line_number if evidence else None,
                    code_snippet=evidence.snippet if evidence else None,
                    agent="Agent_Scanner",
                )
            )

        return AuditReport(
            health_score=score_summary["health_score"],
            security_score=score_summary["security_score"],
            reliability_score=score_summary["reliability_score"],
            scalability_score=score_summary["scalability_score"],
            audit_confidence=self.primer.confidence if self.primer else 80,
            primer_summary=self.primer.summary if self.primer else None,
            findings=converted,
        )
