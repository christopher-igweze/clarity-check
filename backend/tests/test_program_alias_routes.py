"""Compatibility tests for canonical /v1/program/* aliases."""

from __future__ import annotations

import os
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")
os.environ.setdefault("CONTROL_PLANE_USE_SUPABASE", "false")

from api.routes import program  # noqa: E402


class ProgramAliasRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = program.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_alias_test"
            return await call_next(request)

        app.include_router(program.router)
        cls.client = TestClient(app)

    def setUp(self) -> None:
        program.limiter.reset()

    def test_campaign_alias_and_week_paths_interoperate(self) -> None:
        create_resp = self.client.post(
            "/v1/program/campaigns",
            json={
                "name": "alias-campaign",
                "repos": ["https://github.com/pallets/flask"],
                "runs_per_repo": 2,
            },
        )
        self.assertEqual(create_resp.status_code, 200)
        campaign_id = create_resp.json()["campaign_id"]

        get_week_resp = self.client.get(f"/v1/program/week7/campaigns/{campaign_id}")
        self.assertEqual(get_week_resp.status_code, 200)
        self.assertEqual(get_week_resp.json()["campaign_id"], campaign_id)

        ingest_week_resp = self.client.post(
            f"/v1/program/week8/campaigns/{campaign_id}/runs",
            json={
                "repo": "https://github.com/pallets/flask",
                "language": "python",
                "run_id": "run-001",
                "status": "completed",
                "duration_ms": 1200,
                "findings_total": 1,
            },
        )
        self.assertEqual(ingest_week_resp.status_code, 200)

        report_alias_resp = self.client.get(f"/v1/program/campaigns/{campaign_id}/report")
        self.assertEqual(report_alias_resp.status_code, 200)
        self.assertIn("summary", report_alias_resp.json())

    def test_policy_and_secrets_alias_paths(self) -> None:
        profile_resp = self.client.post(
            "/v1/program/policy-profiles",
            json={
                "name": "strict",
                "blocked_commands": ["rm -rf"],
                "restricted_paths": ["/.git"],
            },
        )
        self.assertEqual(profile_resp.status_code, 200)
        profile_id = profile_resp.json()["profile_id"]

        policy_check_resp = self.client.post(
            "/v1/program/policy-check",
            json={
                "profile_id": profile_id,
                "command": "rm -rf /tmp/work",
                "path": "/tmp/work",
            },
        )
        self.assertEqual(policy_check_resp.status_code, 200)
        self.assertEqual(policy_check_resp.json()["action"], "BLOCK")

        secret_resp = self.client.post(
            "/v1/program/secrets",
            json={"name": "github_pat", "value": "ghp_test_1234567890"},
        )
        self.assertEqual(secret_resp.status_code, 200)
        secret_id = secret_resp.json()["secret_id"]

        list_resp = self.client.get("/v1/program/secrets")
        self.assertEqual(list_resp.status_code, 200)
        self.assertGreaterEqual(len(list_resp.json()), 1)

        metadata_resp = self.client.get(f"/v1/program/secrets/{secret_id}")
        self.assertEqual(metadata_resp.status_code, 200)
        self.assertEqual(metadata_resp.json()["secret_id"], secret_id)

    def test_release_alias_paths_for_go_live_decision(self) -> None:
        release_id = "release-alias-1"
        checklist_resp = self.client.post(
            "/v1/program/checklist",
            json={
                "release_id": release_id,
                "security_review": True,
                "slo_dashboard": True,
                "rollback_tested": True,
                "docs_complete": True,
                "runbooks_ready": True,
            },
        )
        self.assertEqual(checklist_resp.status_code, 200)

        rollback_resp = self.client.post(
            "/v1/program/rollback-drills",
            json={
                "release_id": release_id,
                "passed": True,
                "duration_minutes": 8,
                "issues_found": [],
            },
        )
        self.assertEqual(rollback_resp.status_code, 200)

        decision_resp = self.client.post(
            "/v1/program/go-live-decision",
            json={
                "release_id": release_id,
                "validation_release_ready": True,
            },
        )
        self.assertEqual(decision_resp.status_code, 200)
        self.assertEqual(decision_resp.json()["status"], "GO")


if __name__ == "__main__":
    unittest.main()
