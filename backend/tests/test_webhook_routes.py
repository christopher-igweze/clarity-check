"""Route-level tests for webhook signature and replay protection."""

from __future__ import annotations

import hmac
import os
import unittest
from hashlib import sha256
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from api.routes import webhook  # noqa: E402


def _signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()
    return f"sha256={digest}"


class WebhookRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.include_router(webhook.router, prefix="/api")
        cls.client = TestClient(app)

    def setUp(self) -> None:
        webhook._seen_deliveries.clear()

    def test_invalid_signature_rejected(self) -> None:
        body = b'{"action":"opened"}'
        with patch.object(webhook.settings, "github_webhook_secret", "secret"):
            resp = self.client.post(
                "/api/webhook/github",
                content=body,
                headers={
                    "X-GitHub-Delivery": "delivery-1",
                    "X-GitHub-Event": "pull_request",
                    "X-Hub-Signature-256": "sha256=bad",
                    "Content-Type": "application/json",
                },
            )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()["detail"]["code"], "webhook_signature_invalid")

    def test_valid_signature_then_replay_detected(self) -> None:
        body = b'{"action":"opened"}'
        with patch.object(webhook.settings, "github_webhook_secret", "secret"):
            signature = _signature("secret", body)
            headers = {
                "X-GitHub-Delivery": "delivery-2",
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json",
            }

            first = self.client.post("/api/webhook/github", content=body, headers=headers)
            second = self.client.post("/api/webhook/github", content=body, headers=headers)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["status"], "ok")
        self.assertEqual(second.status_code, 409)
        self.assertEqual(second.json()["detail"]["code"], "webhook_replay_detected")


if __name__ == "__main__":
    unittest.main()

