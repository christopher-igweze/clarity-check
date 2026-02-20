"""Week 14 e2e: release checklist persistence and retrieval."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week14E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_release_checklist_upsert_and_fetch(self) -> None:
        user = f"week14-user-{uuid4()}"
        release_id = f"release-{uuid4()}"
        headers = {"X-Test-User": user}

        upsert = self.client.post(
            "/v1/program/week14/checklist",
            json={
                "release_id": release_id,
                "security_review": True,
                "slo_dashboard": True,
                "rollback_tested": False,
                "docs_complete": True,
                "runbooks_ready": True,
            },
            headers=headers,
        )
        self.assertEqual(upsert.status_code, 200)
        self.assertFalse(upsert.json()["rollback_tested"])

        get_resp = self.client.get(
            f"/v1/program/week14/checklist/{release_id}",
            headers=headers,
        )
        self.assertEqual(get_resp.status_code, 200)
        checklist = get_resp.json()
        self.assertEqual(checklist["release_id"], release_id)
        self.assertTrue(checklist["security_review"])
        self.assertTrue(checklist["docs_complete"])


if __name__ == "__main__":
    unittest.main()

