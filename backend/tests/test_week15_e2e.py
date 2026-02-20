"""Week 15 e2e: rollback drill capture and retrieval."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week15E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_rollback_drill_upsert_and_get(self) -> None:
        user = f"week15-user-{uuid4()}"
        release_id = f"release-{uuid4()}"
        headers = {"X-Test-User": user}

        upsert_resp = self.client.post(
            "/v1/program/week15/rollback-drills",
            json={
                "release_id": release_id,
                "passed": True,
                "duration_minutes": 12,
                "issues_found": [],
            },
            headers=headers,
        )
        self.assertEqual(upsert_resp.status_code, 200)
        self.assertTrue(upsert_resp.json()["passed"])

        get_resp = self.client.get(
            f"/v1/program/week15/rollback-drills/{release_id}",
            headers=headers,
        )
        self.assertEqual(get_resp.status_code, 200)
        drill = get_resp.json()
        self.assertEqual(drill["release_id"], release_id)
        self.assertEqual(drill["duration_minutes"], 12)
        self.assertTrue(drill["passed"])


if __name__ == "__main__":
    unittest.main()

