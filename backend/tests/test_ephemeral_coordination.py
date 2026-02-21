"""Tests for distributed coordination fallback/fail-closed behavior."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from config import settings  # noqa: E402
from services.ephemeral_coordination import (  # noqa: E402
    CoordinationUnavailableError,
    EphemeralCoordinator,
)


class EphemeralCoordinationTests(unittest.IsolatedAsyncioTestCase):
    async def test_in_process_lease_fallback_when_fail_closed_disabled(self) -> None:
        original = settings.coordination_fail_closed
        settings.coordination_fail_closed = False
        try:
            coordinator = EphemeralCoordinator(redis_url=None)
            claimed = await coordinator.acquire_lease(
                "runtime-build:test-1",
                owner="worker-a",
                ttl_seconds=5,
            )
            self.assertTrue(claimed)

            denied = await coordinator.acquire_lease(
                "runtime-build:test-1",
                owner="worker-b",
                ttl_seconds=5,
            )
            self.assertFalse(denied)

            renewed = await coordinator.renew_lease(
                "runtime-build:test-1",
                owner="worker-a",
                ttl_seconds=5,
            )
            self.assertTrue(renewed)
        finally:
            settings.coordination_fail_closed = original

    async def test_nonce_claim_fails_closed_when_coordination_required(self) -> None:
        original = settings.coordination_fail_closed
        settings.coordination_fail_closed = True
        try:
            coordinator = EphemeralCoordinator(redis_url=None)
            with self.assertRaises(CoordinationUnavailableError):
                await coordinator.claim_nonce("nonce-1", ttl_seconds=60)
        finally:
            settings.coordination_fail_closed = original


if __name__ == "__main__":
    unittest.main()
