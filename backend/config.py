"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the Vibe-to-Production backend."""

    # --- API Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # --- Supabase ---
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_service_key: str = Field(..., description="Supabase service role key")
    supabase_jwt_secret: str = Field(..., description="Supabase JWT secret for token verification")

    # --- OpenRouter (LLM routing) ---
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # --- GitHub Integration ---
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_oauth_scope: str = "repo read:user user:email"
    github_oauth_state_ttl_minutes: int = 15
    github_oauth_state_secret: str | None = None
    github_webhook_secret: str | None = None
    webhook_replay_window_seconds: int = 600

    # --- Daytona (sandbox) ---
    daytona_api_key: str = Field(..., description="Daytona API key")
    daytona_api_url: str = "https://app.daytona.io/api"
    # Optional. If unset, Daytona will use the account/org default target.
    # Some organizations may not have all regions enabled (e.g. "us").
    daytona_target: str | None = None

    # --- Model Selection (OpenRouter model identifiers) ---
    model_scanner: str = "google/gemini-2.5-pro"
    model_planner: str = "anthropic/claude-sonnet-4.5"
    model_builder: str = "deepseek/deepseek-chat"
    model_security: str = "deepseek/deepseek-chat"
    model_educator: str = "anthropic/claude-sonnet-4.5"

    # --- LLM Runtime Limits ---
    # Keep this conservative to avoid OpenRouter credit/max_token failures.
    llm_max_output_tokens: int = 4096

    # --- Sandbox Limits ---
    sandbox_timeout_minutes: int = 30
    sandbox_cpu: int = 2
    sandbox_memory_gb: int = 4
    sandbox_disk_gb: int = 8

    # --- Tier 1 (Free) ---
    tier1_enabled: bool = True
    tier1_assistant_model: str = "google/gemini-2.5-flash-lite"
    tier1_loc_cap: int = 50000
    tier1_monthly_report_cap: int = 10
    tier1_project_cap: int = 3
    tier1_index_ttl_days: int = 30
    tier1_report_ttl_days: int = 7

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
