"""Application configuration loaded from environment variables."""

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

    # --- Daytona (sandbox) ---
    daytona_api_key: str = Field(..., description="Daytona API key")
    daytona_api_url: str = "https://app.daytona.io/api"
    daytona_target: str = "us"

    # --- Model Selection (OpenRouter model identifiers) ---
    model_scanner: str = "google/gemini-2.5-pro"
    model_planner: str = "anthropic/claude-sonnet-4-5-20250929"
    model_builder: str = "deepseek/deepseek-chat"
    model_security: str = "deepseek/deepseek-chat"
    model_educator: str = "anthropic/claude-sonnet-4-5-20250929"

    # --- Sandbox Limits ---
    sandbox_timeout_minutes: int = 30
    sandbox_cpu: int = 2
    sandbox_memory_gb: int = 4
    sandbox_disk_gb: int = 8

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
