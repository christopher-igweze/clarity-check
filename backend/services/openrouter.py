"""OpenRouter LLM client for multi-model routing.

Wraps the OpenRouter API (OpenAI-compatible) so agents can call different
models through a single interface.  Used by the OpenHands LLM config to
route each agent to its designated model.
"""

from __future__ import annotations

from config import settings


def get_llm_config(model: str) -> dict:
    """Return the LLM configuration dict for an OpenHands agent.

    OpenHands uses LiteLLM under the hood, which supports the
    ``openrouter/`` prefix to route through OpenRouter.

    Args:
        model: The OpenRouter model identifier, e.g.
               ``google/gemini-2.5-pro`` or ``deepseek/deepseek-chat``.

    Returns:
        Dict suitable for constructing an ``openhands.sdk.LLM`` instance.
    """
    return {
        "model": f"openrouter/{model}",
        "api_key": settings.openrouter_api_key,
        "base_url": settings.openrouter_base_url,
    }
