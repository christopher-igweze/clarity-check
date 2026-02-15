"""Agent_Builder — The SRE (DeepSeek V3.2).

Performs dynamic analysis: runs the application inside the sandbox,
executes tests, attempts builds, hits endpoints, and captures screenshots.
Produces objective, verifiable proof of what works and what doesn't.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.findings import Finding, ProbeResult, Category, Severity, FindingSource
from services.context_store import ContextStore

from agents.base_agent import BaseVibe2ProdAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Agent_Builder, a Senior Site Reliability Engineer.  You have full
terminal access to a cloned repository at /home/daytona/repo.

Your mission is to DYNAMICALLY PROBE the application — actually run it and
see what happens.  Do not just read code; execute it.

Steps (run each, capture exit code + output):
1. **Dependency Install**: `npm install` (or `pip install -r requirements.txt`)
   — Does it install cleanly?  Note warnings/errors.
2. **Build Test**: `npm run build` (or equivalent)
   — Does it compile?  Capture any build errors.
3. **Unit Tests**: `npm test` (or `pytest`)
   — How many pass/fail?  Capture the summary.
4. **Dependency Audit**: `npm audit --json` (or `pip-audit --format json`)
   — How many known CVEs?
5. **Startup Test**: Try `npm run dev` or `npm start` (kill after 10s)
   — Does the dev server boot without crashing?
6. **Lint Check**: `npx eslint . --format json` (if configured)
   — How many warnings/errors?

For each step, report:
{
  "step": "install" | "build" | "test" | "audit" | "startup" | "lint",
  "passed": true | false,
  "exit_code": 0,
  "stdout": "first 500 chars of stdout",
  "stderr": "first 500 chars of stderr",
  "duration_ms": 1234
}

Also identify any DYNAMIC findings (issues only discoverable by running
the code) as:
{
  "title": "...",
  "description": "...",
  "category": "reliability" | "security" | "scalability",
  "severity": "critical" | "high" | "medium" | "low",
  "source": "dynamic",
  "file_path": "..." (if applicable),
  "line_number": null
}

Output a JSON object with two keys:
{
  "probe_results": [...],
  "findings": [...]
}

Be factual.  Only report what you actually observed — never fabricate results.
"""


class BuilderAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.builder
    model_config_key = "model_builder"
    system_prompt = SYSTEM_PROMPT

    async def run(self) -> tuple[list[ProbeResult], list[Finding]]:
        """Run the dynamic probe and return results + findings."""
        self._log("Starting dynamic probe — running the application...")

        raw_output = await self._run_conversation(
            "Probe the repository at /home/daytona/repo. "
            "Follow your instructions precisely."
        )

        probe_results, findings = self._parse_output(raw_output)

        # Store in context
        self.context.set(
            "probe:results",
            [p.model_dump(mode="json") for p in probe_results],
        )
        self.context.set(
            "findings:builder",
            [f.model_dump(mode="json") for f in findings],
        )

        # Emit probe results
        for p in probe_results:
            status = "PASS" if p.passed else "FAIL"
            level = LogLevel.success if p.passed else LogLevel.error
            self._log(
                f"[{status}] {p.step} (exit {p.exit_code}, {p.duration_ms}ms)",
                level=level,
                event_type=SSEEventType.probe_result,
                data=p.model_dump(mode="json"),
            )

        # Emit dynamic findings
        for f in findings:
            self._log(
                f"[DYNAMIC] [{f.severity.value.upper()}] {f.title}",
                level=LogLevel.warn,
                event_type=SSEEventType.finding,
                data=f.model_dump(mode="json"),
            )

        self._log(
            f"Dynamic probe complete: {sum(1 for p in probe_results if p.passed)}/{len(probe_results)} steps passed, "
            f"{len(findings)} dynamic issues found",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
        )

        return probe_results, findings

    def _parse_output(
        self, raw: str
    ) -> tuple[list[ProbeResult], list[Finding]]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    data = json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    logger.warning("Builder output is not valid JSON")
                    return [], []
            else:
                return [], []

        probes = []
        for item in data.get("probe_results", []):
            try:
                probes.append(
                    ProbeResult(
                        step=item["step"],
                        passed=item.get("passed", False),
                        exit_code=item.get("exit_code", 1),
                        stdout=item.get("stdout", "")[:2000],
                        stderr=item.get("stderr", "")[:2000],
                        duration_ms=item.get("duration_ms", 0),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping malformed probe result: %s", exc)

        findings = []
        for item in data.get("findings", []):
            try:
                findings.append(
                    Finding(
                        title=item.get("title", "Untitled"),
                        description=item.get("description", ""),
                        category=Category(item.get("category", "reliability")),
                        severity=Severity(item.get("severity", "medium")),
                        source=FindingSource.dynamic,
                        file_path=item.get("file_path"),
                        line_number=item.get("line_number"),
                        agent="Agent_Builder",
                    )
                )
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed finding: %s", exc)

        return probes, findings
