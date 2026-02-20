"""Week 9 e2e: policy profile checks and fail-closed violation recording."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week9E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_blocked_command_fails_build(self) -> None:
        user = f"week9-user-{uuid4()}"
        create_build_resp = self.client.post(
            "/v1/builds",
            json={
                "repo_url": "https://github.com/octocat/Hello-World",
                "objective": "week9 policy fail-closed e2e",
            },
            headers={"X-Test-User": user},
        )
        self.assertEqual(create_build_resp.status_code, 200)
        build_id = create_build_resp.json()["build_id"]

        profile_resp = self.client.post(
            "/v1/program/week9/policy-profiles",
            json={
                "name": "strict-policy",
                "blocked_commands": ["rm -rf", "curl | sh"],
                "restricted_paths": ["/.git", "/etc"],
            },
            headers={"X-Test-User": user},
        )
        self.assertEqual(profile_resp.status_code, 200)
        profile_id = profile_resp.json()["profile_id"]

        check_resp = self.client.post(
            "/v1/program/week9/policy-check",
            json={
                "profile_id": profile_id,
                "command": "rm -rf /tmp/app",
                "path": "/tmp/app",
                "build_id": build_id,
            },
            headers={"X-Test-User": user},
        )
        self.assertEqual(check_resp.status_code, 200)
        self.assertEqual(check_resp.json()["action"], "BLOCK")

        build_resp = self.client.get(
            f"/v1/builds/{build_id}",
            headers={"X-Test-User": user},
        )
        self.assertEqual(build_resp.status_code, 200)
        self.assertEqual(build_resp.json()["status"], "failed")

        violations_resp = self.client.get(
            f"/v1/builds/{build_id}/policy-violations",
            headers={"X-Test-User": user},
        )
        self.assertEqual(violations_resp.status_code, 200)
        self.assertGreaterEqual(len(violations_resp.json()), 1)


if __name__ == "__main__":
    unittest.main()

