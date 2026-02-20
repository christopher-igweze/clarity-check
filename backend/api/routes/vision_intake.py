"""Vision intake conversational endpoint (SSE streaming deltas)."""

from __future__ import annotations

import asyncio
import json
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter, rate_limit_string

router = APIRouter()


class VisionIntakeMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class VisionIntakeRequest(BaseModel):
    messages: list[VisionIntakeMessage] = Field(default_factory=list)
    repo_url: str
    vibe_prompt: str | None = None


def _build_reply(request_body: VisionIntakeRequest) -> str:
    user_turns = [m.content.strip() for m in request_body.messages if m.role == "user"]
    answered_questions = max(0, len(user_turns) - 1)
    repo_url = request_body.repo_url

    if answered_questions <= 0:
        return (
            f"Thanks, I have the repo URL ({repo_url}). First question: what is the single most "
            "important user journey that must never break in production?"
        )
    if answered_questions == 1:
        return (
            "Second question: what sensitive data does this app handle (auth secrets, PII, payments, "
            "health), and what failure would be most damaging to user trust?"
        )
    if answered_questions == 2:
        return (
            "Third question: what is your expected scale over the next 3-6 months and what deployment "
            "target are you using? Include any hard uptime/performance constraints."
        )

    return (
        "Great, that gives enough intent context for a grounded scan. Proceed to scan and I will pass "
        "this charter into the planner and remediation guidance."
    )


def _chunk_text(text: str, max_chunk_len: int = 28) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chunk_len and current:
            chunks.append(f"{current} ")
            current = word
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


@router.post("/vision-intake")
@limiter.limit(rate_limit_string())
async def vision_intake(
    request_body: VisionIntakeRequest,
    request: Request,
) -> StreamingResponse:
    _ = request.state.user_id  # Auth middleware enforces presence.
    reply = _build_reply(request_body)
    chunks = _chunk_text(reply)

    async def event_stream():
        for chunk in chunks:
            payload = {"choices": [{"delta": {"content": chunk}}]}
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.015)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

