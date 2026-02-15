"""Base wrapper around the OpenHands SDK for our specialised agents.

Each agent in the swarm (Scanner, Builder, Security, Planner, Educator)
subclasses ``BaseVibe2ProdAgent`` and provides:

* A unique **name** and **system prompt**.
* A **model** identifier routed through OpenRouter.
* A ``run()`` method that drives the OpenHands conversation loop and
  writes results into the shared ``ContextStore``.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable
from uuid import UUID

from pydantic import SecretStr

from openhands.sdk import LLM, Agent, Conversation, Tool, Event
from openhands.tools.terminal import TerminalTool
from openhands.tools.file_editor import FileEditorTool

from config import settings
from models.agent_log import AgentLogEntry, AgentName, LogLevel, SSEEventType
from services.context_store import ContextStore

logger = logging.getLogger(__name__)


class BaseVibe2ProdAgent(ABC):
    """Abstract base for every agent in the swarm."""

    # Subclasses must set these
    agent_name: AgentName
    model_config_key: str  # attribute name on Settings, e.g. "model_scanner"
    system_prompt: str

    def __init__(
        self,
        scan_id: UUID,
        context: ContextStore,
        emit: Callable[[AgentLogEntry], Any],
        workspace_dir: str = "/home/daytona/repo",
    ) -> None:
        self.scan_id = scan_id
        self.context = context
        self.emit = emit
        self.workspace_dir = workspace_dir

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _get_model(self) -> str:
        return getattr(settings, self.model_config_key)

    def _build_llm(self) -> LLM:
        model = self._get_model()
        return LLM(
            model=f"openrouter/{model}",
            api_key=SecretStr(settings.openrouter_api_key),
            base_url=settings.openrouter_base_url,
        )

    def _build_tools(self) -> list[Tool]:
        """Default toolset: terminal + file editor.  Override to customise."""
        return [
            Tool(name=TerminalTool.name),
            Tool(name=FileEditorTool.name),
        ]

    def _log(
        self,
        message: str,
        level: LogLevel = LogLevel.info,
        event_type: SSEEventType = SSEEventType.agent_log,
        data: dict | None = None,
    ) -> None:
        """Emit a log entry to the SSE stream."""
        entry = AgentLogEntry(
            event_type=event_type,
            agent=self.agent_name,
            message=message,
            level=level,
            data=data,
        )
        self.emit(entry)

    # ------------------------------------------------------------------ #
    # Conversation lifecycle
    # ------------------------------------------------------------------ #

    def _on_event(self, event: Event) -> None:
        """Callback for OpenHands conversation events — forward to SSE."""
        self._log(str(event))

    async def _run_conversation(self, prompt: str) -> str:
        """Create an OpenHands conversation, send the prompt, run, return output."""
        llm = self._build_llm()
        agent = Agent(
            llm=llm,
            tools=self._build_tools(),
            system_prompt_filename=None,
        )

        # Prepend our system prompt to the user message
        full_prompt = f"{self.system_prompt}\n\n---\n\n{prompt}"

        conversation = Conversation(
            agent=agent,
            workspace=self.workspace_dir,
            callbacks=[self._on_event],
        )

        self._log(
            f"Starting {self.agent_name.value}",
            event_type=SSEEventType.agent_start,
        )

        # Run in a thread to avoid blocking the async event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._sync_run, conversation, full_prompt)

        # Extract last assistant message as the agent's output
        last_message = self._extract_output(conversation)

        self._log(
            f"{self.agent_name.value} finished",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
        )

        return last_message

    @staticmethod
    def _sync_run(conversation: Conversation, prompt: str) -> None:
        conversation.send_message(prompt)
        conversation.run()

    @staticmethod
    def _extract_output(conversation: Conversation) -> str:
        """Pull the final text output from the conversation."""
        try:
            state = conversation.state
            if state and state.history:
                for event in reversed(state.history):
                    text = getattr(event, "content", None) or getattr(
                        event, "text", None
                    )
                    if text:
                        return str(text)
        except Exception:
            pass
        return ""

    # ------------------------------------------------------------------ #
    # Abstract interface
    # ------------------------------------------------------------------ #

    @abstractmethod
    async def run(self) -> Any:
        """Execute this agent's task, reading from / writing to the ContextStore."""
        ...
