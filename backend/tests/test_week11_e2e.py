"""Week 11 e2e: webhook nonce/timestamp/HMAC replay defense."""

from __future__ import annotations

import time
import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter
from config import settings
from orchestration.program_store import program_store


class Week11E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_webhook_replay_and_timestamp_validation(self) -> None:
        user = f"week11-user-{uuid4()}"
        body = b'{"event":"build.completed","release":"r1"}'
        nonce = f"nonce-{uuid4()}"
        timestamp = int(time.time())
        signature = program_store.build_platform_signature(
            timestamp=timestamp,
            nonce=nonce,
            body=body,
        )
        headers = {
            "X-Test-User": user,
            "X-Platform-Nonce": nonce,
            "X-Platform-Timestamp": str(timestamp),
            "X-Platform-Signature": signature,
            "Content-Type": "application/json",
        }

        accepted = self.client.post(
            "/v1/program/week11/webhook/ingest",
            content=body,
            headers=headers,
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["status"], "accepted")

        replayed = self.client.post(
            "/v1/program/week11/webhook/ingest",
            content=body,
            headers=headers,
        )
        self.assertEqual(replayed.status_code, 409)
        self.assertEqual(replayed.json()["detail"]["code"], "webhook_replay_detected")

        stale_timestamp = timestamp - 999999
        stale_signature = program_store.build_platform_signature(
            timestamp=stale_timestamp,
            nonce=f"nonce-{uuid4()}",
            body=body,
        )
        stale_resp = self.client.post(
            "/v1/program/week11/webhook/ingest",
            content=body,
            headers={
                "X-Test-User": user,
                "X-Platform-Nonce": f"nonce-{uuid4()}",
                "X-Platform-Timestamp": str(stale_timestamp),
                "X-Platform-Signature": stale_signature,
                "Content-Type": "application/json",
            },
        )
        self.assertEqual(stale_resp.status_code, 401)
        self.assertEqual(stale_resp.json()["detail"]["code"], "webhook_timestamp_invalid")

    def test_webhook_fails_closed_when_coordination_unavailable(self) -> None:
        original = settings.coordination_fail_closed
        settings.coordination_fail_closed = True
        try:
            user = f"week11-user-{uuid4()}"
            body = b'{"event":"build.completed","release":"r1"}'
            nonce = f"nonce-{uuid4()}"
            timestamp = int(time.time())
            signature = program_store.build_platform_signature(
                timestamp=timestamp,
                nonce=nonce,
                body=body,
            )
            resp = self.client.post(
                "/v1/program/week11/webhook/ingest",
                content=body,
                headers={
                    "X-Test-User": user,
                    "X-Platform-Nonce": nonce,
                    "X-Platform-Timestamp": str(timestamp),
                    "X-Platform-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
            self.assertEqual(resp.status_code, 503)
            self.assertEqual(resp.json()["detail"]["code"], "coordination_unavailable")
        finally:
            settings.coordination_fail_closed = original


if __name__ == "__main__":
    unittest.main()
