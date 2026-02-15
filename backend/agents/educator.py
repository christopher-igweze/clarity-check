"""Agent_Educator — The Teacher (Claude 4.5 Sonnet).

Generates human-readable education cards for every finding:
- "Why This Matters" — developer-focused technical explanation
- "CTO's Perspective" — business risk framing (revenue, compliance, velocity)

Tone is empathetic and accessible — explains *why*, not just *what*.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from openhands.sdk import Tool
from openhands.tools.terminal import TerminalTool

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.findings import EducationCard
from services.context_store import ContextStore

from agents.base_agent import BaseVibe2ProdAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Agent_Educator, a Technical Writer who makes complex engineering
concepts accessible to non-technical founders and first-time CTOs.

You will receive a list of confirmed findings and action items.
For EACH item, produce:

1. **why_it_matters** (2-3 sentences, developer-level):
   Explain the technical issue concisely.  What's broken, why it's a risk,
   and what the standard practice is.

2. **cto_perspective** (2-3 sentences, business-level):
   Frame the risk in business terms:
   - Revenue impact ("This could cost you $X in fines or lost customers")
   - User trust ("Users will leave if their data leaks")
   - Velocity impact ("This tech debt will slow your team down 3x")
   - Compliance ("This violates SOC 2 / GDPR / PCI-DSS requirements")

Tone: Empathetic, clear, never condescending.  Use analogies where helpful.
Assume the reader is smart but not a developer.

Output a JSON array:
[
  {
    "finding_id": "uuid",
    "why_it_matters": "...",
    "cto_perspective": "..."
  }
]

Return only the JSON array.
"""


class EducatorAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.educator
    model_config_key = "model_educator"
    system_prompt = SYSTEM_PROMPT

    def _build_tools(self) -> list[Tool]:
        """Educator doesn't need terminal — just reasoning."""
        return [Tool(name=TerminalTool.name)]

    async def run(self) -> list[EducationCard]:
        """Generate education cards for all confirmed findings."""
        self._log("Generating education cards for findings...")

        actions = self.context.get("plan:actions", [])
        scanner = self.context.get("findings:scanner", [])
        builder = self.context.get("findings:builder", [])

        # Combine all items the educator should explain
        all_items = actions or (scanner + builder)

        if not all_items:
            self._log("No findings to explain.", level=LogLevel.warn)
            return []

        prompt = (
            "Generate education cards for each of these findings/action items. "
            "Match each card to the item's id (or title if no id).\n\n"
            f"Items:\n{json.dumps(all_items, indent=2)}"
        )

        raw_output = await self._run_conversation(prompt)
        cards = self._parse_output(raw_output)

        self.context.set(
            "education:cards",
            [c.model_dump(mode="json") for c in cards],
        )

        for c in cards:
            self._log(
                f"Education card generated for {str(c.finding_id)[:8]}...",
                event_type=SSEEventType.education_card,
                data=c.model_dump(mode="json"),
            )

        self._log(
            f"Generated {len(cards)} education cards",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
            data={"card_count": len(cards)},
        )

        return cards

    def _parse_output(self, raw: str) -> list[EducationCard]:
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
                    logger.warning("Educator output is not valid JSON")
                    return []
            else:
                return []

        if not isinstance(data, list):
            data = [data]

        cards: list[EducationCard] = []
        for item in data:
            try:
                cards.append(
                    EducationCard(
                        finding_id=item["finding_id"],
                        why_it_matters=item.get("why_it_matters", ""),
                        cto_perspective=item.get("cto_perspective", ""),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping malformed education card: %s", exc)

        return cards
