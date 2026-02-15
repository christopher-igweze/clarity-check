"""Rate limiting for API endpoints."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings

limiter = Limiter(key_func=get_remote_address)


def rate_limit_string() -> str:
    """Return the rate limit string for the configured limit."""
    return f"{settings.rate_limit_per_minute}/minute"
