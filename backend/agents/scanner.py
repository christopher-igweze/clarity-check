"""Agent_Scanner — The Auditor (Gemini 3 Pro).

Ingests the entire repository using Gemini's massive context window.
Runs static analysis tools inside the sandbox (semgrep, npm audit, eslint).
Produces structured findings with file paths, line numbers, and severity.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.findings import Finding, Category, Severity, FindingSource
from services.context_store import ContextStore

from agents.base_agent import BaseVibe2ProdAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Agent_Scanner, a Senior Software Auditor.  You have full terminal
access to a cloned repository at $WORKSPACE_DIR.

Your mission:
1. Run `find . -type f -not -path './.git/*' -not -path './node_modules/*' | sort`
   to get the file tree.
2. Read critical files: package.json (or requirements.txt), entry points,
   config files, environment files, auth modules.
3. Run static analysis:
   - `semgrep --config auto --json .` (if installed)
   - `npm audit --json` (for Node projects)
   - `grep -rn 'sk_live\\|sk_test\\|AKIA\\|password\\s*=' --include='*.ts' --include='*.js' --include='*.py' --include='*.env' .`
4. Identify:
   - SECURITY: hardcoded secrets, API keys, missing auth, SQL injection, XSS
   - RELIABILITY: missing error handling, no tests, no logging, missing env vars
   - SCALABILITY: no connection pooling, no caching, god files (>400 lines),
     circular dependencies, missing indexes

Output ONLY a JSON array of findings.  Each finding must have:
{
  "title": "Short title",
  "description": "Detailed explanation",
  "category": "security" | "reliability" | "scalability",
  "severity": "critical" | "high" | "medium" | "low",
  "source": "static",
  "file_path": "relative/path/to/file",
  "line_number": 42,
  "code_snippet": "the offending line(s)"
}

Be thorough.  Do not hallucinate files or line numbers — verify everything
by reading the actual files.  If a tool is not available, skip it and note
it.  Return the raw JSON array with no markdown fences.
"""


class ScannerAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.scanner
    model_config_key = "model_scanner"
    system_prompt = SYSTEM_PROMPT

    async def run(self) -> list[Finding]:
        """Execute the deep scan and return structured findings."""
        self._log("Beginning deep static analysis of repository...")

        # Build the prompt with any available context
        charter = self.context.get("charter")
        vibe_prompt = self.context.get("vibe_prompt", "")
        project_intake = self.context.get("project_intake")
        primer = self.context.get("primer")

        extra = ""
        if charter:
            extra += f"\n\nProject Charter:\n{json.dumps(charter, indent=2)}"
        if vibe_prompt:
            extra += f"\n\nOriginal Vibe Prompt:\n{vibe_prompt}"
        if project_intake:
            extra += f"\n\nProject Intake:\n{json.dumps(project_intake, indent=2)}"
        if primer:
            extra += f"\n\nPrimer Context:\n{json.dumps(primer, indent=2)}"

        prompt = (
            "Audit the repository at $WORKSPACE_DIR. "
            "Follow your instructions precisely."
            f"{extra}"
        )

        raw_output = await self._run_conversation(prompt)

        # Parse the JSON findings
        findings = self._parse_findings(raw_output)

        self._log(
            f"Scanner found {len(findings)} issues",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
            data={"findings_count": len(findings)},
        )

        # Persist to context store for downstream agents
        self.context.set(
            "findings:scanner",
            [f.model_dump(mode="json") for f in findings],
        )

        # Emit each finding as an SSE event
        for f in findings:
            self._log(
                f"[{f.severity.value.upper()}] {f.title}",
                level=LogLevel.warn if f.severity in (Severity.critical, Severity.high) else LogLevel.info,
                event_type=SSEEventType.finding,
                data=f.model_dump(mode="json"),
            )

        return findings

    def _parse_findings(self, raw: str) -> list[Finding]:
        """Best-effort parse of the agent's JSON output."""
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract a JSON array from the output
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1:
                try:
                    data = json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    logger.warning("Scanner output is not valid JSON")
                    self._log(
                        "Warning: could not parse scanner output as JSON",
                        level=LogLevel.warn,
                    )
                    return []
            else:
                return []

        if not isinstance(data, list):
            data = [data]

        findings: list[Finding] = []
        for item in data:
            try:
                findings.append(
                    Finding(
                        title=item.get("title", "Untitled"),
                        description=item.get("description", ""),
                        category=Category(item.get("category", "reliability")),
                        severity=Severity(item.get("severity", "medium")),
                        source=FindingSource(item.get("source", "static")),
                        file_path=item.get("file_path"),
                        line_number=item.get("line_number"),
                        code_snippet=item.get("code_snippet"),
                        agent="Agent_Scanner",
                    )
                )
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed finding: %s", exc)
        return findings
