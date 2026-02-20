"""Week 8 e2e: campaign run ingestion and benchmark report generation."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week8E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_campaign_report_after_run_ingestion(self) -> None:
        user = f"week8-user-{uuid4()}"
        campaign_resp = self.client.post(
            "/v1/program/week7/campaigns",
            json={
                "name": "week8-benchmark",
                "repos": ["repo-a", "repo-b"],
                "runs_per_repo": 3,
            },
            headers={"X-Test-User": user},
        )
        self.assertEqual(campaign_resp.status_code, 200)
        campaign_id = campaign_resp.json()["campaign_id"]

        runs = [
            {"repo": "repo-a", "language": "python", "run_id": "a1", "status": "completed", "duration_ms": 1000},
            {"repo": "repo-a", "language": "python", "run_id": "a2", "status": "completed", "duration_ms": 1100},
            {"repo": "repo-a", "language": "python", "run_id": "a3", "status": "failed", "duration_ms": 1300},
            {"repo": "repo-b", "language": "node", "run_id": "b1", "status": "completed", "duration_ms": 900},
            {"repo": "repo-b", "language": "node", "run_id": "b2", "status": "completed", "duration_ms": 950},
            {"repo": "repo-b", "language": "node", "run_id": "b3", "status": "completed", "duration_ms": 970},
        ]
        for run in runs:
            ingest_resp = self.client.post(
                f"/v1/program/week8/campaigns/{campaign_id}/runs",
                json=run,
                headers={"X-Test-User": user},
            )
            self.assertEqual(ingest_resp.status_code, 200)

        report_resp = self.client.get(
            f"/v1/program/week8/campaigns/{campaign_id}/report",
            headers={"X-Test-User": user},
        )
        self.assertEqual(report_resp.status_code, 200)
        report = report_resp.json()
        self.assertEqual(report["summary"]["repo_count"], 2)
        self.assertEqual(report["summary"]["run_count"], 6)
        self.assertIn("rubric", report)
        self.assertIn("gate", report)


if __name__ == "__main__":
    unittest.main()

