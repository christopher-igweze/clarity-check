"""Week 16 e2e: go-live decisioning from readiness gates."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week16E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_go_live_decision_go_when_all_gates_pass(self) -> None:
        user = f"week16-user-{uuid4()}"
        release_id = f"release-{uuid4()}"
        headers = {"X-Test-User": user}

        checklist_resp = self.client.post(
            "/v1/program/week14/checklist",
            json={
                "release_id": release_id,
                "security_review": True,
                "slo_dashboard": True,
                "rollback_tested": True,
                "docs_complete": True,
                "runbooks_ready": True,
            },
            headers=headers,
        )
        self.assertEqual(checklist_resp.status_code, 200)

        rollback_resp = self.client.post(
            "/v1/program/week15/rollback-drills",
            json={
                "release_id": release_id,
                "passed": True,
                "duration_minutes": 8,
                "issues_found": [],
            },
            headers=headers,
        )
        self.assertEqual(rollback_resp.status_code, 200)

        decision_resp = self.client.post(
            "/v1/program/week16/go-live-decision",
            json={
                "release_id": release_id,
                "validation_release_ready": True,
            },
            headers=headers,
        )
        self.assertEqual(decision_resp.status_code, 200)
        self.assertEqual(decision_resp.json()["status"], "GO")
        self.assertEqual(decision_resp.json()["reasons"], [])

        fetch_resp = self.client.get(
            f"/v1/program/week16/go-live-decision/{release_id}",
            headers=headers,
        )
        self.assertEqual(fetch_resp.status_code, 200)
        self.assertEqual(fetch_resp.json()["status"], "GO")


if __name__ == "__main__":
    unittest.main()

