"""Pydantic models for org onboarding payloads."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TechnicalLevel(str, Enum):
    founder = "founder"
    vibe_coder = "vibe_coder"
    engineer = "engineer"


class ExplanationStyle(str, Enum):
    teach_me = "teach_me"
    just_steps = "just_steps"
    cto_brief = "cto_brief"


class ShippingPosture(str, Enum):
    ship_fast = "ship_fast"
    balanced = "balanced"
    production_first = "production_first"


class AcquisitionSource(str, Enum):
    x_twitter = "x_twitter"
    linkedin = "linkedin"
    tiktok = "tiktok"
    youtube = "youtube"
    reddit = "reddit"
    discord = "discord"
    product_hunt = "product_hunt"
    indie_hackers = "indie_hackers"
    hacker_news = "hacker_news"
    google_search = "google_search"
    newsletter_email = "newsletter_email"
    referral = "referral"
    founder_begged_me = "founder_begged_me"
    other = "other"


class CodingAgentProvider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class OrgOnboardingPayload(BaseModel):
    """Org-profile defaults captured during required onboarding."""

    technical_level: TechnicalLevel
    explanation_style: ExplanationStyle
    shipping_posture: ShippingPosture = ShippingPosture.balanced
    tool_tags: list[str] = Field(default_factory=list, max_length=30)
    acquisition_source: AcquisitionSource
    acquisition_other: str | None = None
    coding_agent_provider: CodingAgentProvider
    coding_agent_model: str = Field(min_length=1, max_length=200)
