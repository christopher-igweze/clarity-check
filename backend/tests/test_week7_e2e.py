"""Week 7 e2e: validation campaign creation and retrieval."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week7E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_create_and_get_validation_campaign(self) -> None:
        user = f"week7-user-{uuid4()}"
        create_resp = self.client.post(
            "/v1/program/week7/campaigns",
            json={
                "name": "week7-os-validation",
                "repos": [
                    "https://github.com/pallets/flask",
                    "https://github.com/expressjs/express",
                ],
                "runs_per_repo": 3,
            },
            headers={"X-Test-User": user},
        )
        self.assertEqual(create_resp.status_code, 200)
        campaign = create_resp.json()
        self.assertEqual(campaign["name"], "week7-os-validation")
        self.assertEqual(len(campaign["repos"]), 2)

        get_resp = self.client.get(
            f"/v1/program/week7/campaigns/{campaign['campaign_id']}",
            headers={"X-Test-User": user},
        )
        self.assertEqual(get_resp.status_code, 200)
        fetched = get_resp.json()
        self.assertEqual(fetched["campaign_id"], campaign["campaign_id"])
        self.assertEqual(fetched["runs_per_repo"], 3)


if __name__ == "__main__":
    unittest.main()

