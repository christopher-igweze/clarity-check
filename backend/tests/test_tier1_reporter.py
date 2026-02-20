"""Unit tests for Tier 1 report synthesis."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from tier1.contracts import Tier1Evidence, Tier1Finding
from tier1.reporter import Tier1Reporter


def _warn_finding() -> Tier1Finding:
    return Tier1Finding(
        check_id="REL_002",
        status="warn",
        category="reliability",
        severity="medium",
        engine="index",
        confidence=0.9,
        title="Missing CI workflow",
        description="No .github/workflows pipeline was detected.",
        evidence=[
            Tier1Evidence(
                file_path=".github/workflows",
                line_number=None,
                snippet="No workflow files found",
                match="missing_ci",
            )
        ],
        suggested_fix_stub="Add CI workflow to run lint/test/build.",
    )


class Tier1ReporterTests(unittest.IsolatedAsyncioTestCase):
    async def test_generate_report_includes_rich_sections_and_cost(self) -> None:
        reporter = Tier1Reporter()
        findings = [_warn_finding()]

        fake_context = {
            "executive_summary": "This repo is stable but missing CI guardrails.",
            "educational_moments": ["CI prevents regressions from shipping silently."],
            "risk_narrative": "Without CI, each change carries higher operational risk.",
        }
        fake_usage = {"prompt_tokens": 1200, "completion_tokens": 300, "total_tokens": 1500}

        with patch.object(
            reporter,
            "_generate_assistant_context",
            new=AsyncMock(return_value=(fake_context, fake_usage)),
        ):
            artifact = await reporter.generate_report(
                findings=findings,
                score_summary={
                    "health_score": 91,
                    "security_score": 100,
                    "reliability_score": 84,
                    "scalability_score": 90,
                },
                intake_context={
                    "product_summary": "Demo product",
                    "target_users": "Engineering teams",
                },
                user_preferences={
                    "technical_level": "founder",
                    "explanation_style": "teach_me",
                    "shipping_posture": "balanced",
                    "coding_agent_provider": "anthropic",
                    "coding_agent_model": "anthropic/claude-sonnet-4.5",
                },
                run_details={
                    "scan_id": "scan-123",
                    "repo_sha": "abc123",
                    "index_source": "fresh",
                    "cache_hit": False,
                    "file_count": 42,
                    "loc_total": 7600,
                    "index_ms": 2200,
                    "scan_ms": 180,
                    "total_before_report_ms": 2500,
                    "reports_generated_before": 1,
                    "report_limit": 10,
                },
                git_metadata={
                    "history_available": True,
                    "commit_count_90d": 34,
                    "contributors_90d": 4,
                    "top_churn_files_90d": [{"file_path": "src/main.py", "touch_count": 8}],
                    "latest_commit_at": "2026-02-15T00:00:00+00:00",
                },
                index_facts={
                    "has_ci": False,
                    "has_tests": True,
                    "lockfiles_present": ["poetry.lock"],
                },
            )

        markdown = artifact.markdown
        self.assertIn("## What You're Doing Well", markdown)
        self.assertIn("## Top Findings", markdown)
        self.assertIn("## Educational Guidance", markdown)
        self.assertIn("## Coding Agent Execution Plan", markdown)
        self.assertIn("Coding agent prompt:", markdown)
        self.assertIn("## Run Details", markdown)
        self.assertIn("## Personalization Profile", markdown)
        self.assertIn("![Score profile chart](data:image/png;base64,", markdown)
        self.assertIn("![Findings by severity chart](data:image/png;base64,", markdown)
        self.assertIn("Monthly usage before this run: 1 / 10 reports", markdown)
        self.assertIn("Copy the prompt block below into your coding agent as-is.", artifact.agent_markdown)
        self.assertIn("```text", artifact.agent_markdown)
        self.assertIn("Target provider: anthropic", artifact.agent_markdown)
        self.assertIn("Target model: anthropic/claude-sonnet-4.5", artifact.agent_markdown)
        self.assertIn("Do not ask follow-up questions.", artifact.agent_markdown)
        self.assertIn("docs/agent-implementation-note.md", artifact.agent_markdown)
        self.assertIn("\"asked_follow_up_questions\": false", artifact.agent_markdown)
        self.assertIn("\"branch_name\": \"actual branch name\"", artifact.agent_markdown)
        self.assertIsNotNone(artifact.pdf_base64)
        self.assertTrue(str(artifact.pdf_base64).startswith("JVBER"))

        run_details = artifact.summary_json["run_details"]
        self.assertGreater(run_details["total_ms"], run_details["scan_ms"])
        self.assertGreater(run_details["cost_breakdown"]["total_usd"], 0.0)
        self.assertEqual(run_details["model_usage"]["total_tokens"], 1500)
        self.assertFalse(artifact.fallback_used)
        self.assertIsNotNone(artifact.model_used)

    async def test_generate_report_falls_back_without_model_response(self) -> None:
        reporter = Tier1Reporter()

        with patch.object(
            reporter,
            "_generate_assistant_context",
            new=AsyncMock(side_effect=RuntimeError("model failed")),
        ):
            artifact = await reporter.generate_report(
                findings=[],
                score_summary={
                    "health_score": 100,
                    "security_score": 100,
                    "reliability_score": 100,
                    "scalability_score": 100,
                },
                intake_context={"product_summary": "Clean repo", "target_users": "internal"},
                user_preferences=None,
                run_details={"scan_id": "scan-xyz", "total_before_report_ms": 10},
                git_metadata={},
                index_facts={},
            )

        self.assertTrue(artifact.fallback_used)
        self.assertIsNone(artifact.model_used)
        self.assertIn("No warnings or failures were detected.", artifact.markdown)
        self.assertIn("No actionable findings were detected in this scan.", artifact.agent_markdown)
        usage = artifact.summary_json["run_details"]["model_usage"]
        self.assertEqual(usage["total_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
