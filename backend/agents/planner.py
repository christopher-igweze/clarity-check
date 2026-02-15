"""Agent_Planner — The Architect (Claude 4.5 Opus).

Reviews all findings from Scanner, Builder, and Security agents.
Produces a prioritised remediation plan with step-by-step fix
instructions, effort estimates, and dependency ordering.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.findings import ActionItem, Category, Severity
from services.context_store import ContextStore

from agents.base_agent import BaseVibe2ProdAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Agent_Planner, a Principal Software Architect.  You have full
terminal access to a cloned repository at /home/daytona/repo.

You will receive:
- Findings from Agent_Scanner (static analysis)
- Probe results from Agent_Builder (dynamic analysis)
- Security verdicts from Agent_Security (validated findings)

Your mission:
1. **Review all findings** and discard any that were rejected by Security.
2. **Prioritise by business impact**:
   - Critical: data loss, money loss, security breach
   - High: app crashes under load, missing auth on sensitive routes
   - Medium: poor performance, missing logging
   - Low: code style, minor warnings
3. **For each confirmed issue, produce a detailed action item**:
   - Clear title
   - Why it matters (1 sentence)
   - Step-by-step fix instructions (be specific: which file, what to change)
   - Effort estimate: "quick" (<5 min), "moderate" (15-30 min), "significant" (1+ hr)
   - Dependencies (which other fixes should be done first)
4. **Group and order** the items so the most impactful, lowest-effort items
   come first (quick wins).

Output a JSON array of action items:
[
  {
    "title": "...",
    "description": "Why this matters and what to do",
    "category": "security" | "reliability" | "scalability",
    "severity": "critical" | "high" | "medium" | "low",
    "priority": 1,
    "effort": "quick" | "moderate" | "significant",
    "fix_steps": ["Step 1: ...", "Step 2: ...", ...],
    "dependencies": [],
    "file_path": "...",
    "line_number": null
  }
]

Read the actual code to verify your fix steps are accurate.  Do not suggest
fixes for files that don't exist.  Return only the JSON array.
"""


class PlannerAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.planner
    model_config_key = "model_planner"
    system_prompt = SYSTEM_PROMPT

    async def run(self) -> list[ActionItem]:
        """Generate prioritised remediation plan."""
        self._log("Generating remediation plan from all findings...")

        scanner = self.context.get("findings:scanner", [])
        builder = self.context.get("findings:builder", [])
        probes = self.context.get("probe:results", [])
        verdicts = self.context.get("findings:security_verdicts", [])
        new_sec = self.context.get("findings:security_new", [])

        prompt = (
            "Create a prioritised remediation plan based on these inputs.\n\n"
            f"Scanner findings:\n{json.dumps(scanner, indent=2)}\n\n"
            f"Builder findings:\n{json.dumps(builder, indent=2)}\n\n"
            f"Probe results:\n{json.dumps(probes, indent=2)}\n\n"
            f"Security verdicts:\n{json.dumps(verdicts, indent=2)}\n\n"
            f"New security findings:\n{json.dumps(new_sec, indent=2)}"
        )

        raw_output = await self._run_conversation(prompt)
        action_items = self._parse_output(raw_output)

        self.context.set(
            "plan:actions",
            [a.model_dump(mode="json") for a in action_items],
        )

        for item in action_items:
            self._log(
                f"[P{item.priority}] [{item.severity.value.upper()}] {item.title} "
                f"({item.effort})",
                level=LogLevel.info,
                event_type=SSEEventType.action_item,
                data=item.model_dump(mode="json"),
            )

        self._log(
            f"Remediation plan: {len(action_items)} action items generated",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
            data={"action_count": len(action_items)},
        )

        return action_items

    def _parse_output(self, raw: str) -> list[ActionItem]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1:
                try:
                    data = json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    logger.warning("Planner output is not valid JSON")
                    return []
            else:
                return []

        if not isinstance(data, list):
            data = [data]

        items: list[ActionItem] = []
        for idx, item in enumerate(data, start=1):
            try:
                items.append(
                    ActionItem(
                        title=item.get("title", "Untitled"),
                        description=item.get("description", ""),
                        category=Category(item.get("category", "reliability")),
                        severity=Severity(item.get("severity", "medium")),
                        priority=item.get("priority", idx),
                        effort=item.get("effort", "moderate"),
                        fix_steps=item.get("fix_steps", []),
                        file_path=item.get("file_path"),
                        line_number=item.get("line_number"),
                    )
                )
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed action item: %s", exc)

        return items
