"""Agent_Security — The Gatekeeper (DeepSeek V3.2).

Validates Scanner and Builder findings.  Eliminates false positives,
deepens the security analysis with OWASP Top 10 checks, and produces
confidence-scored verdicts.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.findings import Finding, SecurityVerdict
from services.context_store import ContextStore

from agents.base_agent import BaseVibe2ProdAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Agent_Security, a Senior Application Security Engineer and Gatekeeper.
You have full terminal access to a cloned repository at $WORKSPACE_DIR.

You will be given a list of findings from Agent_Scanner and Agent_Builder.
Your job:

1. **Validate each finding** — read the actual file and line number to confirm
   or reject the finding.  Eliminate false positives.
2. **Deepen the analysis** — look for additional security issues the Scanner
   may have missed:
   - OWASP Top 10: SQL injection, XSS, CSRF, SSRF, auth bypass, broken
     access control, security misconfiguration
   - Hardcoded secrets (API keys, passwords, tokens, private keys)
   - Insecure direct object references
   - Missing security headers
   - Insecure deserialization
   - Outdated dependencies with known CVEs
3. **Check auth flows** — is JWT validation correct?  Are routes protected?
   Are there open admin endpoints?

For each finding you reviewed, output:
{
  "finding_id": "uuid-from-original-finding",
  "confirmed": true | false,
  "confidence": 0-100,
  "notes": "Why you confirmed/rejected, or additional context"
}

Also output any NEW findings you discovered (same format as Scanner findings).

Return JSON:
{
  "verdicts": [...],
  "new_findings": [...]
}

Be precise.  Read the actual code before making a judgement.  Never guess.
"""


class SecurityAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.security
    model_config_key = "model_security"
    system_prompt = SYSTEM_PROMPT

    async def run(self) -> tuple[list[SecurityVerdict], list[Finding]]:
        """Validate existing findings and surface new security issues."""
        self._log("Security review: validating findings and scanning for threats...")

        # Gather findings from upstream agents
        scanner_findings = self.context.get("findings:scanner", [])
        builder_findings = self.context.get("findings:builder", [])
        all_findings = scanner_findings + builder_findings

        prompt = (
            "Review the following findings from the Scanner and Builder agents. "
            "Validate each one by reading the actual code, and look for any "
            "additional security issues.\n\n"
            f"Findings to review:\n{json.dumps(all_findings, indent=2)}"
        )

        raw_output = await self._run_conversation(prompt)
        verdicts, new_findings = self._parse_output(raw_output)

        # Store validated findings
        confirmed_ids = {
            str(v.finding_id) for v in verdicts if v.confirmed
        }
        self.context.set(
            "findings:security_verdicts",
            [v.model_dump(mode="json") for v in verdicts],
        )
        if new_findings:
            self.context.set(
                "findings:security_new",
                [f.model_dump(mode="json") for f in new_findings],
            )

        # Emit verdicts
        confirmed_count = sum(1 for v in verdicts if v.confirmed)
        rejected_count = sum(1 for v in verdicts if not v.confirmed)
        self._log(
            f"Security review: {confirmed_count} confirmed, {rejected_count} rejected, "
            f"{len(new_findings)} new issues found",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
            data={
                "confirmed": confirmed_count,
                "rejected": rejected_count,
                "new_findings": len(new_findings),
            },
        )

        for v in verdicts:
            status = "CONFIRMED" if v.confirmed else "REJECTED"
            self._log(
                f"[{status}] Finding {str(v.finding_id)[:8]}... "
                f"(confidence: {v.confidence}%) — {v.notes[:100]}",
                level=LogLevel.warn if v.confirmed else LogLevel.info,
                event_type=SSEEventType.security_verdict,
                data=v.model_dump(mode="json"),
            )

        return verdicts, new_findings

    def _parse_output(
        self, raw: str
    ) -> tuple[list[SecurityVerdict], list[Finding]]:
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
                    logger.warning("Security output is not valid JSON")
                    return [], []
            else:
                return [], []

        verdicts = []
        for item in data.get("verdicts", []):
            try:
                verdicts.append(
                    SecurityVerdict(
                        finding_id=item["finding_id"],
                        confirmed=item.get("confirmed", False),
                        confidence=item.get("confidence", 50),
                        notes=item.get("notes", ""),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping malformed verdict: %s", exc)

        from models.findings import Category, Severity, FindingSource

        new_findings = []
        for item in data.get("new_findings", []):
            try:
                new_findings.append(
                    Finding(
                        title=item.get("title", "Untitled"),
                        description=item.get("description", ""),
                        category=Category(item.get("category", "security")),
                        severity=Severity(item.get("severity", "high")),
                        source=FindingSource.static,
                        file_path=item.get("file_path"),
                        line_number=item.get("line_number"),
                        agent="Agent_Security",
                    )
                )
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed finding: %s", exc)

        return verdicts, new_findings
