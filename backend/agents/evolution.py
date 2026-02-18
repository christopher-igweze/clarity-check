"""Agent_Evolution — behavioral analysis from Git history.

Computes CodeScene-style signals:
- hotspots (high-churn files)
- change coupling (files that frequently change together)
- ownership risk (single-author concentration)
"""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.evolution import ChangeCoupling, EvolutionReport, Hotspot, OwnershipRisk
from models.findings import Category, Finding, FindingSource, Severity

from agents.base_agent import BaseVibe2ProdAgent


class EvolutionAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.evolution
    model_config_key = "model_planner"  # Unused; deterministic agent.
    system_prompt = "Deterministic behavioral analysis agent."

    async def run(self) -> tuple[EvolutionReport, list[Finding]]:
        self._log("Running behavioral analysis from Git history...")

        report = self._build_report()
        findings = self._to_findings(report)

        self.context.set("evolution:report", report.model_dump(mode="json"))
        self.context.set(
            "findings:evolution",
            [f.model_dump(mode="json") for f in findings],
        )

        self._log(
            "Behavioral analysis complete",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
            data={
                "hotspots": len(report.hotspots),
                "change_coupling": len(report.change_coupling),
                "ownership_risk": len(report.ownership_risk),
                "findings_count": len(findings),
            },
        )

        for finding in findings:
            self._log(
                f"[{finding.severity.value.upper()}] {finding.title}",
                level=LogLevel.warn,
                event_type=SSEEventType.finding,
                data=finding.model_dump(mode="json"),
            )

        return report, findings

    def _build_report(self) -> EvolutionReport:
        workspace = Path(self.workspace_dir)
        if not workspace.exists() or not (workspace / ".git").exists():
            self._log(
                "No git metadata found in workspace; skipping behavioral analysis.",
                level=LogLevel.warn,
            )
            return EvolutionReport()

        # Collect commits from the most recent 120 entries.
        raw = self._run_git(
            [
                "log",
                "--name-only",
                "--pretty=format:__COMMIT__",
                "--max-count=120",
            ]
        )
        commit_files = self._parse_commit_files(raw)

        if not commit_files:
            return EvolutionReport()

        # Hotspots: top files by change count.
        file_counter = Counter()
        for files in commit_files:
            file_counter.update(files)
        hotspots = [
            Hotspot(file_path=path, change_count=count)
            for path, count in file_counter.most_common(8)
        ]

        # Change coupling: file pairs that co-occur in commits.
        pair_counter: Counter[tuple[str, str]] = Counter()
        for files in commit_files:
            unique = sorted(set(files))[:20]
            for i in range(len(unique)):
                for j in range(i + 1, len(unique)):
                    pair_counter[(unique[i], unique[j])] += 1
        coupling = [
            ChangeCoupling(file_a=a, file_b=b, co_change_count=count)
            for (a, b), count in pair_counter.most_common(8)
            if count >= 2
        ]

        # Ownership risk on top hotspots.
        ownership = []
        for hs in hotspots[:6]:
            out = self._run_git(
                ["log", "--format=%an", "--max-count=120", "--", hs.file_path]
            )
            authors = [a.strip() for a in out.splitlines() if a.strip()]
            if not authors:
                continue
            counts = Counter(authors)
            primary, primary_count = counts.most_common(1)[0]
            share = int(round((primary_count / len(authors)) * 100))
            if share >= 70:
                ownership.append(
                    OwnershipRisk(
                        file_path=hs.file_path,
                        primary_author=primary,
                        primary_author_share=share,
                    )
                )

        return EvolutionReport(
            hotspots=hotspots,
            change_coupling=coupling,
            ownership_risk=ownership,
        )

    def _to_findings(self, report: EvolutionReport) -> list[Finding]:
        findings: list[Finding] = []

        for hs in report.hotspots[:5]:
            severity = Severity.high if hs.change_count >= 20 else Severity.medium
            findings.append(
                Finding(
                    title=f"Hotspot file: {hs.file_path}",
                    description=(
                        f"This file changed {hs.change_count} times in recent history. "
                        "High-churn files are strong candidates for refactoring guards "
                        "and regression tests before major edits."
                    ),
                    category=Category.scalability,
                    severity=severity,
                    source=FindingSource.static,
                    file_path=hs.file_path,
                    agent=self.agent_name.value,
                )
            )

        for cp in report.change_coupling[:3]:
            findings.append(
                Finding(
                    title="Tight change coupling detected",
                    description=(
                        f"`{cp.file_a}` and `{cp.file_b}` changed together "
                        f"{cp.co_change_count} times. This suggests hidden coupling and "
                        "higher regression risk when touching either file."
                    ),
                    category=Category.reliability,
                    severity=Severity.medium,
                    source=FindingSource.static,
                    file_path=cp.file_a,
                    agent=self.agent_name.value,
                )
            )

        for risk in report.ownership_risk[:3]:
            findings.append(
                Finding(
                    title="Knowledge silo risk",
                    description=(
                        f"{risk.primary_author} authored ~{risk.primary_author_share}% of "
                        f"recent changes in `{risk.file_path}`. Documenting or pairing on "
                        "this area reduces bus-factor risk."
                    ),
                    category=Category.scalability,
                    severity=Severity.medium,
                    source=FindingSource.static,
                    file_path=risk.file_path,
                    agent=self.agent_name.value,
                )
            )

        return findings

    def _run_git(self, args: list[str]) -> str:
        try:
            proc = subprocess.run(
                ["git", *args],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            return proc.stdout or ""
        except Exception:
            return ""

    @staticmethod
    def _parse_commit_files(raw: str) -> list[list[str]]:
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if line == "__COMMIT__":
                if current:
                    blocks.append(current)
                current = []
                continue
            if line.startswith(".git/"):
                continue
            current.append(line)
        if current:
            blocks.append(current)
        return blocks
