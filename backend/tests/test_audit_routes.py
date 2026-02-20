"""Route-level tests for Tier 1 audit API behavior."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

# Avoid importing the deep orchestrator dependency tree (requires openhands).
if "agents.orchestrator" not in sys.modules:
    import types

    fake_orchestrator = types.ModuleType("agents.orchestrator")

    class _FakeAuditOrchestrator:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def run(self):
            raise RuntimeError("deep orchestrator should not be used in Tier 1 route tests")

    fake_orchestrator.AuditOrchestrator = _FakeAuditOrchestrator
    sys.modules["agents.orchestrator"] = fake_orchestrator

from api.routes import audit  # noqa: E402
from tier1.contracts import Tier1QuotaStatus  # noqa: E402


class AuditRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = FastAPI()
        app.state.limiter = audit.limiter

        @app.middleware("http")
        async def _inject_user(request, call_next):
            request.state.user_id = "user_test"
            return await call_next(request)

        app.include_router(audit.router, prefix="/api")
        cls.client = TestClient(app)

    @staticmethod
    def _payload() -> dict:
        return {
            "repo_url": "https://github.com/octocat/Hello-World",
            "project_intake": {
                "project_origin": "external",
                "product_summary": "Small demo application.",
                "target_users": "Developers",
                "sensitive_data": ["none"],
                "must_not_break_flows": ["Landing page load"],
                "deployment_target": "Vercel",
                "scale_expectation": "MVP / low traffic",
            },
        }

    def test_onboarding_incomplete_blocks_audit(self) -> None:
        with patch.object(audit.settings, "tier1_enabled", True), patch(
            "api.routes.audit.db.get_github_access_token", new=AsyncMock(return_value=None)
        ), patch("api.routes.audit.db.is_onboarding_complete", new=AsyncMock(return_value=False)):
            resp = self.client.post("/api/audit", json=self._payload())

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"]["code"], "onboarding_required")

    def test_project_cap_blocks_new_project(self) -> None:
        with patch.object(audit.settings, "tier1_enabled", True), patch(
            "api.routes.audit.db.get_github_access_token", new=AsyncMock(return_value=None)
        ), patch("api.routes.audit.db.is_onboarding_complete", new=AsyncMock(return_value=True)), patch(
            "api.routes.audit.db.get_project_by_repo_url", new=AsyncMock(return_value=None)
        ), patch(
            "api.routes.audit.db.get_active_project_count",
            new=AsyncMock(return_value=audit.settings.tier1_project_cap),
        ):
            resp = self.client.post("/api/audit", json=self._payload())

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"]["code"], "limit_projects_exceeded")

    def test_loc_cap_blocks_large_repo(self) -> None:
        repo_info = SimpleNamespace(
            full_name="octocat/Hello-World",
            default_branch="master",
            clone_url="https://github.com/octocat/Hello-World.git",
        )

        with patch.object(audit.settings, "tier1_enabled", True), patch(
            "api.routes.audit.db.get_github_access_token", new=AsyncMock(return_value=None)
        ), patch("api.routes.audit.db.is_onboarding_complete", new=AsyncMock(return_value=True)), patch(
            "api.routes.audit.db.get_project_by_repo_url", new=AsyncMock(return_value=None)
        ), patch(
            "api.routes.audit.db.get_active_project_count", new=AsyncMock(return_value=0)
        ), patch(
            "api.routes.audit.db.get_or_create_free_usage_month",
            new=AsyncMock(return_value={"reports_generated": 0}),
        ), patch(
            "api.routes.audit.parse_repo_url", new=AsyncMock(return_value=("octocat", "Hello-World"))
        ), patch("api.routes.audit.get_repo_info", new=AsyncMock(return_value=repo_info)), patch(
            "api.routes.audit.get_head_sha", new=AsyncMock(return_value="abc123")
        ), patch(
            "api.routes.audit.DeterministicIndexer.build_or_reuse",
            new=AsyncMock(return_value={"loc_total": 60001, "file_count": 12}),
        ):
            resp = self.client.post("/api/audit", json=self._payload())

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"]["code"], "limit_loc_exceeded")

    def test_reports_cap_blocks_when_monthly_quota_used(self) -> None:
        with patch.object(audit.settings, "tier1_enabled", True), patch(
            "api.routes.audit.db.get_github_access_token", new=AsyncMock(return_value=None)
        ), patch("api.routes.audit.db.is_onboarding_complete", new=AsyncMock(return_value=True)), patch(
            "api.routes.audit.db.get_project_by_repo_url", new=AsyncMock(return_value=None)
        ), patch(
            "api.routes.audit.db.get_active_project_count", new=AsyncMock(return_value=0)
        ), patch(
            "api.routes.audit.db.get_or_create_free_usage_month",
            new=AsyncMock(return_value={"reports_generated": audit.settings.tier1_monthly_report_cap}),
        ):
            resp = self.client.post("/api/audit", json=self._payload())

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"]["code"], "limit_reports_exceeded")

    def test_limits_endpoint_returns_expected_fields(self) -> None:
        quota = Tier1QuotaStatus(
            month_key=date(2026, 2, 1),
            reports_generated=3,
            reports_limit=10,
            reports_remaining=7,
            project_count=2,
            project_limit=3,
            loc_cap=50000,
        )

        with patch("api.routes.audit.get_quota_status", new=AsyncMock(return_value=quota)):
            resp = self.client.get("/api/limits")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["tier"], "free")
        self.assertEqual(body["month_key"], "2026-02-01")
        self.assertEqual(body["reports_generated"], 3)
        self.assertEqual(body["reports_remaining"], 7)
        self.assertEqual(body["project_limit"], 3)
        self.assertEqual(body["loc_cap"], 50000)

    def test_report_artifact_missing_returns_404(self) -> None:
        scan_id = uuid4()
        with patch(
            "api.routes.audit.db.get_report_artifact", new=AsyncMock(return_value=None)
        ):
            resp = self.client.get(f"/api/report-artifacts/{scan_id}")

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["detail"]["code"], "report_artifact_missing")

    def test_report_artifact_returns_markdown(self) -> None:
        scan_id = uuid4()
        artifact = {
            "artifact_type": "markdown",
            "content": "# Report\n\nHello",
            "expires_at": datetime.now(timezone.utc).isoformat(),
        }

        with patch(
            "api.routes.audit.db.get_report_artifact", new=AsyncMock(return_value=artifact)
        ):
            resp = self.client.get(f"/api/report-artifacts/{scan_id}")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["artifact_type"], "markdown")
        self.assertIn("# Report", body["content"])
        self.assertEqual(body["content_encoding"], "utf-8")
        self.assertEqual(body["mime_type"], "text/markdown")

    def test_report_artifact_returns_pdf_payload(self) -> None:
        scan_id = uuid4()
        artifact = {
            "artifact_type": "pdf",
            "content": "JVBERi0xLjQK",
            "expires_at": datetime.now(timezone.utc).isoformat(),
        }

        mock_get = AsyncMock(return_value=artifact)
        with patch("api.routes.audit.db.get_report_artifact", new=mock_get):
            resp = self.client.get(f"/api/report-artifacts/{scan_id}?artifact_type=pdf")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["artifact_type"], "pdf")
        self.assertEqual(body["content_encoding"], "base64")
        self.assertEqual(body["mime_type"], "application/pdf")
        mock_get.assert_awaited_once_with(scan_id, "user_test", "pdf")

    def test_report_artifact_invalid_type_returns_400(self) -> None:
        scan_id = uuid4()
        resp = self.client.get(f"/api/report-artifacts/{scan_id}?artifact_type=zip")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["detail"]["code"], "report_artifact_type_invalid")

    def test_start_audit_returns_quota_remaining_for_free_tier(self) -> None:
        project_id = uuid4()
        repo_info = SimpleNamespace(
            full_name="octocat/Hello-World",
            default_branch="master",
            clone_url="https://github.com/octocat/Hello-World.git",
        )
        existing_project = {"id": str(project_id)}

        with patch.object(audit.settings, "tier1_enabled", True), patch(
            "api.routes.audit._maybe_cleanup_tier1", new=AsyncMock()
        ), patch(
            "api.routes.audit._run_tier1_audit", new=AsyncMock()
        ), patch(
            "api.routes.audit.db.get_github_access_token", new=AsyncMock(return_value=None)
        ), patch("api.routes.audit.db.is_onboarding_complete", new=AsyncMock(return_value=True)), patch(
            "api.routes.audit.db.get_project_by_repo_url", new=AsyncMock(return_value=existing_project)
        ), patch(
            "api.routes.audit.db.get_active_project_count", new=AsyncMock(return_value=1)
        ), patch(
            "api.routes.audit.db.get_or_create_free_usage_month",
            new=AsyncMock(return_value={"reports_generated": 2}),
        ), patch(
            "api.routes.audit.parse_repo_url", new=AsyncMock(return_value=("octocat", "Hello-World"))
        ), patch("api.routes.audit.get_repo_info", new=AsyncMock(return_value=repo_info)), patch(
            "api.routes.audit.get_head_sha", new=AsyncMock(return_value="abc123")
        ), patch(
            "api.routes.audit.DeterministicIndexer.build_or_reuse",
            new=AsyncMock(return_value={"loc_total": 1200, "file_count": 42}),
        ), patch(
            "api.routes.audit.db.create_scan_report", new=AsyncMock(return_value=uuid4())
        ):
            resp = self.client.post("/api/audit", json=self._payload())

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["tier"], "free")
        self.assertEqual(body["quota_remaining"], 8)


if __name__ == "__main__":
    unittest.main()
