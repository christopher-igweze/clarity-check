"""Master orchestrator — manages the full agent pipeline for an audit.

The orchestrator:
1. Provisions a Daytona sandbox
2. Runs agents in sequence (Scanner → Evolution → Builder → Security → Planner → Educator)
3. Passes data between agents via the ContextStore (no token bloat)
4. Streams all events to the frontend via an SSE callback
5. Assembles the final AuditReport
6. Persists everything to Supabase
7. Tears down the sandbox
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable
from uuid import UUID
import shutil
from pathlib import Path
import subprocess

from models.agent_log import AgentLogEntry, AgentName, LogLevel, SSEEventType
from models.findings import (
    AuditReport,
    Finding,
    Severity,
    Category,
)
from models.evolution import EvolutionReport
from models.scan import PrimerResult, ProjectIntake
from services.context_store import ContextStore
from services.github import parse_repo_url, get_repo_info
from sandbox.manager import SandboxManager

from agents.scanner import ScannerAgent
from agents.evolution import EvolutionAgent
from agents.builder import BuilderAgent
from agents.security import SecurityAgent
from agents.planner import PlannerAgent
from agents.educator import EducatorAgent

logger = logging.getLogger(__name__)


class AuditOrchestrator:
    """Drives the full audit pipeline for a single scan."""

    def __init__(
        self,
        scan_id: UUID,
        repo_url: str,
        emit: Callable[[AgentLogEntry], Any],
        vibe_prompt: str | None = None,
        project_charter: dict | None = None,
        project_intake: ProjectIntake | None = None,
        primer: PrimerResult | None = None,
        github_token: str | None = None,
    ) -> None:
        self.scan_id = scan_id
        self.repo_url = repo_url
        self.emit = emit
        self.vibe_prompt = vibe_prompt
        self.project_charter = project_charter
        self.project_intake = project_intake
        self.primer = primer
        self.github_token = github_token

        self.context = ContextStore(scan_id)
        self.sandbox_mgr = SandboxManager()

    # ------------------------------------------------------------------ #
    # Logging helpers
    # ------------------------------------------------------------------ #

    def _log(
        self,
        message: str,
        level: LogLevel = LogLevel.info,
        event_type: SSEEventType = SSEEventType.agent_log,
        data: dict | None = None,
    ) -> None:
        entry = AgentLogEntry(
            event_type=event_type,
            agent=AgentName.orchestrator,
            message=message,
            level=level,
            data=data,
        )
        self.emit(entry)

    # ------------------------------------------------------------------ #
    # Main pipeline
    # ------------------------------------------------------------------ #

    async def run(self) -> AuditReport:
        """Execute the full audit and return the assembled report."""
        local_workspace_root = Path("/tmp") / "clarity-check" / str(self.scan_id)
        workspace_dir = str(local_workspace_root / "repo")

        try:
            # ---- 0. Seed context ----
            if self.vibe_prompt:
                self.context.set("vibe_prompt", self.vibe_prompt)
            if self.project_charter:
                self.context.set("charter", self.project_charter)
            if self.project_intake:
                self.context.set("project_intake", self.project_intake.model_dump(mode="json"))
            if self.primer:
                self.context.set("primer", self.primer.model_dump(mode="json"))

            # ---- 1. Provision sandbox ----
            self._log("Provisioning sandbox environment...")
            owner, repo = await parse_repo_url(self.repo_url)
            repo_info = await get_repo_info(owner, repo, self.github_token)
            clone_url = repo_info.clone_url

            # Prepare a local clone for OpenHands tools (TerminalTool/FileEditorTool)
            # Running those tools inside the API container requires a writable path.
            await self._prepare_local_repo(local_workspace_root, clone_url, repo_info.default_branch)

            session = await self.sandbox_mgr.provision(self.scan_id, clone_url)
            self._log(
                f"Sandbox ready. Repo cloned: {repo_info.full_name}",
                level=LogLevel.success,
            )

            # ---- 2. Agent_Scanner (The Auditor) ----
            scanner = ScannerAgent(
                scan_id=self.scan_id,
                context=self.context,
                emit=self.emit,
                workspace_dir=workspace_dir,
            )
            scanner_findings = await scanner.run()

            # ---- 3. Agent_Evolution (Behavioral analysis) ----
            evolution = EvolutionAgent(
                scan_id=self.scan_id,
                context=self.context,
                emit=self.emit,
                workspace_dir=workspace_dir,
            )
            evolution_report, evolution_findings = await evolution.run()

            # ---- 4. Agent_Builder (The SRE) ----
            probe_results = []
            builder_findings: list[Finding] = []

            builder = BuilderAgent(
                scan_id=self.scan_id,
                context=self.context,
                emit=self.emit,
                workspace_dir=workspace_dir,
            )
            probe_results, builder_findings = await builder.run()

            # ---- 5. Agent_Security (The Gatekeeper) ----
            security = SecurityAgent(
                scan_id=self.scan_id,
                context=self.context,
                emit=self.emit,
                workspace_dir=workspace_dir,
            )
            verdicts, new_sec_findings = await security.run()

            # ---- 6. Agent_Planner (The Architect) ----
            planner = PlannerAgent(
                scan_id=self.scan_id,
                context=self.context,
                emit=self.emit,
                workspace_dir=workspace_dir,
            )
            action_items = await planner.run()

            # ---- 7. Agent_Educator (The Teacher) ----
            educator = EducatorAgent(
                scan_id=self.scan_id,
                context=self.context,
                emit=self.emit,
                workspace_dir=workspace_dir,
            )
            education_cards = await educator.run()

            # ---- 8. Assemble report ----
            all_findings = (
                scanner_findings + evolution_findings + builder_findings + new_sec_findings
            )

            report = self._assemble_report(
                findings=all_findings,
                probe_results=probe_results,
                evolution=evolution_report,
            )
            report.action_items = action_items
            report.education_cards = education_cards
            report.security_verdicts = verdicts
            if self.primer:
                report.primer_summary = self.primer.summary or None
                report.audit_confidence = self.primer.confidence

            self._log(
                f"Audit complete. Health score: {report.health_score}/100",
                level=LogLevel.success,
                event_type=SSEEventType.scan_complete,
                data={
                    "health_score": report.health_score,
                    "security_score": report.security_score,
                    "reliability_score": report.reliability_score,
                    "scalability_score": report.scalability_score,
                    "findings_count": len(all_findings),
                    "action_items_count": len(action_items),
                },
            )

            return report

        except Exception as exc:
            logger.exception("Audit failed for scan %s", self.scan_id)
            self._log(
                f"Audit failed: {exc}",
                level=LogLevel.error,
                event_type=SSEEventType.scan_error,
            )
            raise

        finally:
            # ---- 9. Teardown ----
            await self.sandbox_mgr.destroy(self.scan_id)
            self.context.clear()
            try:
                shutil.rmtree(local_workspace_root, ignore_errors=True)
            except Exception:
                logger.exception("Failed to delete local workspace %s", local_workspace_root)

    @staticmethod
    async def _prepare_local_repo(workspace_root: Path, clone_url: str, branch: str) -> None:
        """Clone the repo into a local, writable workspace for OpenHands tools."""
        repo_dir = workspace_root / "repo"

        def _sync_clone() -> None:
            shutil.rmtree(workspace_root, ignore_errors=True)
            workspace_root.mkdir(parents=True, exist_ok=True)
            # Shallow clone for speed.
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, clone_url, str(repo_dir)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        await asyncio.to_thread(_sync_clone)

    # ------------------------------------------------------------------ #
    # Scoring
    # ------------------------------------------------------------------ #

    def _assemble_report(
        self,
        findings: list[Finding],
        probe_results: list,
        evolution: EvolutionReport | None = None,
    ) -> AuditReport:
        """Calculate scores and build the report."""
        security_score = self._category_score(findings, Category.security)
        reliability_score = self._category_score(findings, Category.reliability)
        scalability_score = self._category_score(findings, Category.scalability)

        # Probe results affect reliability
        if probe_results:
            passed = sum(1 for p in probe_results if p.passed)
            total = len(probe_results)
            probe_factor = passed / total if total else 1.0
            reliability_score = int(reliability_score * (0.5 + 0.5 * probe_factor))

        health_score = int(
            security_score * 0.40
            + reliability_score * 0.35
            + scalability_score * 0.25
        )

        return AuditReport(
            health_score=max(0, min(100, health_score)),
            security_score=max(0, min(100, security_score)),
            reliability_score=max(0, min(100, reliability_score)),
            scalability_score=max(0, min(100, scalability_score)),
            evolution=evolution or EvolutionReport(),
            findings=findings,
            probe_results=probe_results,
        )

    @staticmethod
    def _category_score(findings: list[Finding], category: Category) -> int:
        """Start at 100, deduct points per finding by severity."""
        score = 100
        deductions = {
            Severity.critical: 25,
            Severity.high: 15,
            Severity.medium: 8,
            Severity.low: 3,
        }
        for f in findings:
            if f.category == category:
                score -= deductions.get(f.severity, 5)
        return max(0, score)
