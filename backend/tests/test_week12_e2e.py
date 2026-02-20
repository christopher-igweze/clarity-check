"""Week 12 e2e: idempotent checkpoint creation for retry-safe operations."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week12E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_idempotent_checkpoint_reuses_first_checkpoint(self) -> None:
        user = f"week12-user-{uuid4()}"
        build_resp = self.client.post(
            "/v1/builds",
            json={
                "repo_url": "https://github.com/octocat/week12-e2e",
                "objective": "week12 idempotency e2e",
            },
            headers={"X-Test-User": user},
        )
        self.assertEqual(build_resp.status_code, 200)
        build_id = build_resp.json()["build_id"]

        request_payload = {
            "build_id": build_id,
            "idempotency_key": "week12-checkpoint-key",
            "reason": "checkpoint_for_retry_safe_resume",
        }
        first = self.client.post(
            "/v1/program/week12/idempotent-checkpoints",
            json=request_payload,
            headers={"X-Test-User": user},
        )
        self.assertEqual(first.status_code, 200)
        self.assertFalse(first.json()["replayed"])

        second = self.client.post(
            "/v1/program/week12/idempotent-checkpoints",
            json=request_payload,
            headers={"X-Test-User": user},
        )
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json()["replayed"])
        self.assertEqual(second.json()["checkpoint_id"], first.json()["checkpoint_id"])


if __name__ == "__main__":
    unittest.main()

