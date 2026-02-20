"""Week 13 e2e: SLO summary generation from build lifecycle outcomes."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week13E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_slo_summary_reflects_completed_and_aborted_runs(self) -> None:
        user = f"week13-user-{uuid4()}"
        headers = {"X-Test-User": user}

        aborted_build = self.client.post(
            "/v1/builds",
            json={"repo_url": "https://github.com/octocat/slo-abort", "objective": "abort build"},
            headers=headers,
        )
        self.assertEqual(aborted_build.status_code, 200)
        aborted_build_id = aborted_build.json()["build_id"]
        abort_resp = self.client.post(
            f"/v1/builds/{aborted_build_id}/abort",
            json={"reason": "week13 aborted control sample"},
            headers=headers,
        )
        self.assertEqual(abort_resp.status_code, 200)

        completed_build = self.client.post(
            "/v1/builds",
            json={"repo_url": "https://github.com/octocat/slo-complete", "objective": "complete build"},
            headers=headers,
        )
        self.assertEqual(completed_build.status_code, 200)
        completed_build_id = completed_build.json()["build_id"]

        bootstrap = self.client.post(
            f"/v1/builds/{completed_build_id}/runtime/bootstrap",
            headers=headers,
        )
        self.assertEqual(bootstrap.status_code, 200)

        finished = False
        for _ in range(8):
            tick = self.client.post(
                f"/v1/builds/{completed_build_id}/runtime/tick",
                headers=headers,
            )
            self.assertEqual(tick.status_code, 200)
            if tick.json()["finished"] is True:
                finished = True
                break
        self.assertTrue(finished)

        slo_resp = self.client.get("/v1/program/week13/slo-summary", headers=headers)
        self.assertEqual(slo_resp.status_code, 200)
        slo = slo_resp.json()
        self.assertGreaterEqual(slo["total_builds"], 2)
        self.assertGreaterEqual(slo["completed_builds"], 1)
        self.assertGreaterEqual(slo["aborted_builds"], 1)
        self.assertGreater(slo["success_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()

