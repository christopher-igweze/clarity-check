"""Tier 1 assistant report synthesis with deterministic structure."""

from __future__ import annotations

import base64
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO

import httpx

from config import settings
from tier1.contracts import Tier1Finding, Tier1ReportArtifact

logger = logging.getLogger(__name__)

DAYTONA_VCPU_PER_SEC_USD = 0.000014
DAYTONA_RAM_GB_PER_SEC_USD = 0.0000045
LLM_INPUT_PER_MILLION_USD = 0.10
LLM_OUTPUT_PER_MILLION_USD = 0.40


class Tier1Reporter:
    async def generate_report(
        self,
        *,
        findings: list[Tier1Finding],
        score_summary: dict,
        intake_context: dict,
        user_preferences: dict | None = None,
        run_details: dict | None = None,
        git_metadata: dict | None = None,
        index_facts: dict | None = None,
    ) -> Tier1ReportArtifact:
        report_started_perf = time.perf_counter()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.tier1_report_ttl_days)

        run_details = dict(run_details or {})
        git_metadata = dict(git_metadata or {})
        index_facts = dict(index_facts or {})

        actionable = self._prioritize_findings(
            [f for f in findings if f.status in {"warn", "fail"}],
            git_metadata,
        )
        strengths = self._build_strengths(findings, score_summary, index_facts, git_metadata)
        execution_plan = self._build_execution_plan(actionable, git_metadata)
        shipping_posture = (user_preferences or {}).get("shipping_posture") or "balanced"
        launch_guidance = self._launch_recommendation(actionable, shipping_posture)

        model_usage = None
        assistant_context = None
        model_used: str | None = None
        fallback_used = False

        try:
            assistant_context, model_usage = await self._generate_assistant_context(
                findings=actionable,
                score_summary=score_summary,
                intake_context=intake_context,
                user_preferences=user_preferences,
            )
            model_used = settings.tier1_assistant_model
        except Exception:
            logger.exception("Tier1 assistant context generation failed; using deterministic-only narrative")
            fallback_used = True

        report_ms = int((time.perf_counter() - report_started_perf) * 1000)
        run_details_enriched = self._finalize_run_details(
            run_details=run_details,
            report_ms=report_ms,
            model_usage=model_usage,
        )

        markdown = self._compose_report_markdown(
            score_summary=score_summary,
            intake_context=intake_context,
            user_preferences=user_preferences,
            strengths=strengths,
            actionable_findings=actionable,
            execution_plan=execution_plan,
            assistant_context=assistant_context,
            run_details=run_details_enriched,
            git_metadata=git_metadata,
            model_usage=run_details_enriched.get("model_usage"),
        )
        agent_markdown = self._compose_agent_markdown(
            intake_context=intake_context,
            user_preferences=user_preferences,
            actionable_findings=actionable,
            execution_plan=execution_plan,
            launch_guidance=launch_guidance,
            run_details=run_details_enriched,
        )
        pdf_base64 = self._compose_report_pdf_base64(
            intake_context=intake_context,
            score_summary=score_summary,
            strengths=strengths,
            actionable_findings=actionable,
            execution_plan=execution_plan,
            launch_guidance=launch_guidance,
            run_details=run_details_enriched,
        )

        summary_json = {
            "scores": score_summary,
            "counts": {
                "findings_total": len(actionable),
                "by_severity": self._counts_by(actionable, "severity"),
                "by_category": self._counts_by(actionable, "category"),
            },
            "strengths": strengths,
            "execution_plan": execution_plan,
            "run_details": {
                **run_details_enriched,
                "git_metadata": git_metadata,
            },
            "next_steps": [
                "Triage high-severity findings and assign an owner.",
                "Execute the coding-agent plan and capture test evidence in each PR.",
                "Re-run Tier 1 scan to verify score movement and close resolved findings.",
            ],
        }

        return Tier1ReportArtifact(
            markdown=markdown,
            agent_markdown=agent_markdown,
            pdf_base64=pdf_base64,
            summary_json=summary_json,
            expires_at=expires_at,
            model_used=model_used,
            fallback_used=fallback_used,
        )

    async def _generate_assistant_context(
        self,
        *,
        findings: list[Tier1Finding],
        score_summary: dict,
        intake_context: dict,
        user_preferences: dict | None,
    ) -> tuple[dict, dict | None]:
        style_guide = self._style_guide(user_preferences)
        prompt_payload = {
            "style_guide": style_guide,
            "scores": score_summary,
            "intake": intake_context,
            "findings": [f.model_dump(mode="json") for f in findings[:10]],
        }

        prompt = (
            "You are Clarity Check's educational CTO assistant. "
            "Return ONLY valid JSON with keys: executive_summary, educational_moments (array of short strings), risk_narrative. "
            "Keep it concise and directly actionable.\n\n"
            f"{json.dumps(prompt_payload)[:22000]}"
        )

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.tier1_assistant_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 800,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else None

        parsed = self._parse_assistant_json(content)
        if not isinstance(parsed, dict):
            raise ValueError("Assistant response was not a JSON object")

        parsed.setdefault("executive_summary", "")
        parsed.setdefault("educational_moments", [])
        parsed.setdefault("risk_narrative", "")
        return parsed, usage

    @staticmethod
    def _parse_assistant_json(content: str) -> dict:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Assistant response did not contain JSON object delimiters")

        candidate = content[start : end + 1]
        parsed = json.loads(candidate)
        if not isinstance(parsed, dict):
            raise ValueError("Assistant response JSON was not an object")
        return parsed

    def _compose_report_markdown(
        self,
        *,
        score_summary: dict,
        intake_context: dict,
        user_preferences: dict | None,
        strengths: list[str],
        actionable_findings: list[Tier1Finding],
        execution_plan: list[dict],
        assistant_context: dict | None,
        run_details: dict,
        git_metadata: dict,
        model_usage: dict | None,
    ) -> str:
        product_summary = intake_context.get("product_summary", "Unknown project")
        target_users = intake_context.get("target_users", "Unknown users")
        explanation_style = (user_preferences or {}).get("explanation_style") or "just_steps"
        technical_level = (user_preferences or {}).get("technical_level") or "engineer"
        shipping_posture = (user_preferences or {}).get("shipping_posture") or "balanced"

        high_or_critical = sum(
            1 for finding in actionable_findings if finding.severity in {"high", "critical"}
        )
        launch_guidance = self._launch_recommendation(actionable_findings, shipping_posture)
        finding_count = len(actionable_findings)
        finding_word = "finding" if finding_count == 1 else "findings"

        lines: list[str] = [
            f"# Clarity Check Report: {product_summary}",
            "",
            "## Executive Summary",
        ]
        score_chart_uri = self._score_profile_png_data_uri(score_summary)
        severity_chart_uri = self._severity_profile_png_data_uri(actionable_findings)

        if actionable_findings:
            top = actionable_findings[0]
            lines.extend(
                [
                    (
                        "- Baseline: **Strong across core dimensions**; one targeted gap remains."
                        if finding_count == 1 and score_summary.get("health_score", 0) >= 90
                        else "- Baseline: Quality is mixed; multiple issues need coordinated fixes."
                    ),
                    f"- Status: **Action required**. {finding_count} {finding_word}, including {high_or_critical} high/critical.",
                    f"- Highest priority: **{top.check_id} — {top.title}**",
                    f"- Why now: {self._business_impact_for_finding(top)}",
                    f"- Launch recommendation: **{launch_guidance['decision']}**. {launch_guidance['reason']}",
                ]
            )
        else:
            lines.append("- Status: **Healthy baseline**. No warnings or failures in this run.")
            lines.append("- Launch recommendation: **Proceed**. No blocking issues detected in this scan.")

        lines.extend(
            [
                "",
                "## Score Breakdown",
                f"- Health score: **{score_summary.get('health_score', 0)} / 100**",
                f"- Security score: **{score_summary.get('security_score', 0)}**",
                f"- Reliability score: **{score_summary.get('reliability_score', 0)}**",
                f"- Scalability score: **{score_summary.get('scalability_score', 0)}**",
                f"- Audience: **{target_users}**",
                "",
                "## Visual Snapshot",
                f"- Health: {score_summary.get('health_score', 0)} / 100",
                f"- Security: {score_summary.get('security_score', 0)} / 100",
                f"- Reliability: {score_summary.get('reliability_score', 0)} / 100",
                f"- Scalability: {score_summary.get('scalability_score', 0)} / 100",
                f"- Severity mix: {self._severity_mix_line(actionable_findings)}",
                "",
                "## Visual Charts",
            ]
        )
        if score_chart_uri:
            lines.extend(
                [
                    "- Score profile:",
                    f"![Score profile chart]({score_chart_uri})",
                ]
            )
        else:
            lines.append("- Score profile image unavailable in this environment.")

        if severity_chart_uri:
            lines.extend(
                [
                    "- Findings by severity:",
                    f"![Findings by severity chart]({severity_chart_uri})",
                ]
            )
        else:
            lines.append("- Findings-by-severity image unavailable in this environment.")

        lines.extend(
            [
                "",
                "## What You're Doing Well",
            ]
        )

        if strengths:
            lines.extend([f"- {item}" for item in strengths])
        else:
            lines.append("- Core quality checks are currently stable.")

        lines.extend(["", "## Top Findings"])
        if not actionable_findings:
            lines.append("- No warnings or failures were detected.")
        else:
            for idx, finding in enumerate(actionable_findings[:10], start=1):
                hotspot = self._hotspot_context_for_finding(finding, git_metadata)
                lines.append(
                    f"### {idx}. {finding.check_id} — {finding.title} ({finding.severity.upper()} / {finding.status.upper()})"
                )
                lines.append(f"- Why this matters: {self._business_impact_for_finding(finding)}")
                if hotspot:
                    lines.append(f"- Change pattern: {hotspot}")
                lines.append(f"- What we saw: {finding.description}")
                lines.append(f"- Evidence: {self._format_evidence(finding)}")
                lines.append(f"- Suggested fix: {finding.suggested_fix_stub}")

        lines.extend(["", "## Educational Guidance"])
        lines.extend(
            self._default_educational_guidance(
                actionable_findings,
                explanation_style,
                technical_level,
            )
        )
        if assistant_context and assistant_context.get("educational_moments"):
            for moment in assistant_context.get("educational_moments", [])[:3]:
                lines.append(f"- Extra context: {moment}")

        lines.extend(["", "## Coding Agent Execution Plan"])
        if execution_plan:
            for idx, item in enumerate(execution_plan, start=1):
                lines.append(f"### Task {idx}: {item['title']}")
                lines.append(f"- Outcome: {item['objective']}")
                lines.append(f"- Estimated effort: **{item['estimate']}**")
                lines.append(f"- Deliverables: {item['deliverables']}")
                lines.append(f"- Steps: {item['steps']}")
                lines.append(f"- Verification: {item['verification']}")
                lines.append("- Coding agent prompt:")
                lines.append("```text")
                lines.append(item["agent_prompt"])
                lines.append("```")
        else:
            lines.append("- No remediation tasks required for this run.")

        lines.extend(["", "## Run Details"])
        lines.append(f"- Scan id: `{run_details.get('scan_id', 'unknown')}`")
        lines.append(f"- Repo SHA: `{run_details.get('repo_sha', 'unknown')}`")
        lines.append(
            f"- Indexing mode: **{run_details.get('index_source', 'fresh')}** (cache hit: {run_details.get('cache_hit', False)})"
        )
        if run_details.get("index_generated_at"):
            lines.append(f"- Index generated at: {run_details.get('index_generated_at')}")
        lines.append(f"- Files scanned: **{run_details.get('file_count', 0)}**")
        lines.append(f"- LOC scanned: **{run_details.get('loc_total', 0)}**")
        lines.append(
            f"- Timings (ms): index={run_details.get('index_ms', 0)}, scan={run_details.get('scan_ms', 0)}, report={run_details.get('report_ms', 0)}, total={run_details.get('total_ms', 0)}"
        )
        if run_details.get("reports_generated_before") is not None:
            lines.append(
                f"- Monthly usage before this run: {run_details.get('reports_generated_before')} / {run_details.get('report_limit', 0)} reports"
            )

        cost = run_details.get("cost_breakdown") or {}
        lines.append(
            f"- Estimated cost (USD): compute={cost.get('compute_usd', 0):.4f}, llm={cost.get('llm_usd', 0):.4f}, total={cost.get('total_usd', 0):.4f}"
        )
        usage = model_usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        lines.append(
            f"- LLM usage: prompt_tokens={usage.get('prompt_tokens', 0)}, completion_tokens={usage.get('completion_tokens', 0)}, total_tokens={usage.get('total_tokens', 0)}"
        )

        lines.extend(["", "## Personalization Profile"])
        lines.append(f"- Technical level: **{technical_level}**")
        lines.append(f"- Explanation style: **{explanation_style}**")
        lines.append(f"- Shipping posture: **{shipping_posture}**")

        lines.extend(
            [
                "",
                "## Risk Narrative",
                self._compose_risk_narrative(
                    findings=actionable_findings,
                    target_users=target_users,
                    launch_guidance=launch_guidance,
                ),
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def _counts_by(findings: list[Tier1Finding], field: str) -> dict:
        out: dict[str, int] = {}
        for finding in findings:
            key = str(getattr(finding, field, "unknown"))
            out[key] = out.get(key, 0) + 1
        return out

    def _prioritize_findings(self, findings: list[Tier1Finding], git_metadata: dict) -> list[Tier1Finding]:
        churn_rows = list(git_metadata.get("top_churn_files_90d") or [])
        churn_rank = {
            str(row.get("file_path")): idx
            for idx, row in enumerate(churn_rows)
            if row.get("file_path")
        }

        def _hotspot_rank(finding: Tier1Finding) -> int:
            if not finding.evidence:
                return 999
            ranks = [churn_rank.get(ev.file_path, 999) for ev in finding.evidence if ev.file_path]
            return min(ranks) if ranks else 999

        return sorted(findings, key=lambda finding: (*self._finding_priority_key(finding), _hotspot_rank(finding)))

    @staticmethod
    def _score_bar(value: int, width: int = 16) -> str:
        clamped = max(0, min(100, int(value)))
        filled = int(round((clamped / 100.0) * width))
        return f"[{'#' * filled}{'.' * (width - filled)}]"

    @staticmethod
    def _severity_mix_line(findings: list[Tier1Finding]) -> str:
        if not findings:
            return "none"
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            if finding.severity in counts:
                counts[finding.severity] += 1
        return (
            f"critical={counts['critical']}, high={counts['high']}, "
            f"medium={counts['medium']}, low={counts['low']}"
        )

    @staticmethod
    def _score_profile_png_data_uri(score_summary: dict) -> str | None:
        image = Tier1Reporter._score_profile_png_image(score_summary)
        if image is None:
            return None
        return Tier1Reporter._image_to_data_uri(image)

    @staticmethod
    def _severity_profile_png_data_uri(findings: list[Tier1Finding]) -> str | None:
        image = Tier1Reporter._severity_profile_png_image(findings)
        if image is None:
            return None
        return Tier1Reporter._image_to_data_uri(image)

    @staticmethod
    def _score_profile_png_image(score_summary: dict):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception:
            return None

        image = Image.new("RGB", (920, 320), "#0f172a")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        draw.text((24, 18), "Score Profile (higher is better)", fill="#e5e7eb", font=font)
        labels = [
            ("Health", int(score_summary.get("health_score", 0)), "#22c55e"),
            ("Security", int(score_summary.get("security_score", 0)), "#ef4444"),
            ("Reliability", int(score_summary.get("reliability_score", 0)), "#38bdf8"),
            ("Scalability", int(score_summary.get("scalability_score", 0)), "#f59e0b"),
        ]
        start_x = 190
        max_width = 680
        bar_h = 32
        gap = 22
        y = 56

        for label, value, color in labels:
            clamped = max(0, min(100, value))
            draw.text((24, y + 10), label, fill="#cbd5e1", font=font)
            draw.rounded_rectangle((start_x, y, start_x + max_width, y + bar_h), radius=8, fill="#1f2937")
            filled_w = int((clamped / 100.0) * max_width)
            if filled_w > 0:
                draw.rounded_rectangle((start_x, y, start_x + filled_w, y + bar_h), radius=8, fill=color)
            draw.text((start_x + max_width + 12, y + 10), str(clamped), fill="#e5e7eb", font=font)
            y += bar_h + gap

        return image

    @staticmethod
    def _severity_profile_png_image(findings: list[Tier1Finding]):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception:
            return None

        image = Image.new("RGB", (920, 320), "#0f172a")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        draw.text((24, 18), "Actionable Findings by Severity", fill="#e5e7eb", font=font)

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            if finding.severity in counts:
                counts[finding.severity] += 1

        max_count = max(1, max(counts.values()) if counts else 0)
        chart_left = 80
        chart_right = 860
        chart_top = 60
        chart_bottom = 260
        draw.line((chart_left, chart_top, chart_left, chart_bottom), fill="#64748b", width=2)
        draw.line((chart_left, chart_bottom, chart_right, chart_bottom), fill="#64748b", width=2)

        severities = [
            ("critical", "#ef4444"),
            ("high", "#f97316"),
            ("medium", "#eab308"),
            ("low", "#22c55e"),
        ]
        slot_w = (chart_right - chart_left - 40) // len(severities)
        bar_w = max(36, slot_w // 2)

        for idx, (name, color) in enumerate(severities):
            count = counts.get(name, 0)
            x_center = chart_left + 30 + idx * slot_w + slot_w // 2
            x0 = x_center - bar_w // 2
            x1 = x_center + bar_w // 2
            bar_h = int((count / max_count) * (chart_bottom - chart_top - 10)) if count > 0 else 0
            y0 = chart_bottom - bar_h
            if bar_h > 0:
                draw.rectangle((x0, y0, x1, chart_bottom), fill=color)
            draw.text((x_center - 16, chart_bottom + 10), name, fill="#cbd5e1", font=font)
            draw.text((x_center - 6, y0 - 16), str(count), fill="#e5e7eb", font=font)

        return image

    @staticmethod
    def _image_to_data_uri(image) -> str:
        buf = BytesIO()
        image.save(buf, format="PNG", optimize=True)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def _compose_agent_markdown(
        self,
        *,
        intake_context: dict,
        user_preferences: dict | None,
        actionable_findings: list[Tier1Finding],
        execution_plan: list[dict],
        launch_guidance: dict,
        run_details: dict,
    ) -> str:
        product_summary = intake_context.get("product_summary", "Unknown project")
        repo_target_users = intake_context.get("target_users", "engineering team")
        prefs = user_preferences or {}
        provider = str(prefs.get("coding_agent_provider") or "openai").strip().lower()
        model = str(prefs.get("coding_agent_model") or self._default_model_for_provider(provider)).strip()
        run_id = str(run_details.get("scan_id", "unknown"))
        branch_name = (
            f"codex/{self._slug_for_branch(product_summary, 24)}-"
            f"{self._slug_for_branch('fix', 8)}-"
            f"{self._slug_for_branch(run_id, 16)}"
        )
        provider_overlay = self._provider_packet_overlay(provider, model)
        implementation_doc = "docs/agent-implementation-note.md"

        lines: list[str] = [
            f"# Agent Execution Packet: {product_summary}",
            "",
            "Copy the prompt block below into your coding agent as-is.",
            "",
            "```text",
            "You are a senior software engineer fixing audit findings in a production codebase in one pass.",
            f"Project: {product_summary}",
            f"Audience impacted: {repo_target_users}",
            f"Target provider: {provider}",
            f"Target model: {model}",
            f"Launch recommendation: {launch_guidance.get('decision')} - {launch_guidance.get('reason')}",
            "",
            "Provider-specific overlay:",
            *[f"- {row}" for row in provider_overlay],
            "",
            "Hard constraints (non-negotiable):",
            "- Keep changes minimal and scoped to the findings.",
            "- Add or update tests for every fix.",
            "- Do not ask follow-up questions. Make safe assumptions, document them, and proceed.",
            "- Do not disable tests, CI checks, or safety controls.",
            "- Create and switch to branch: "
            f"`{branch_name}`.",
            f"- Create or update `{implementation_doc}` with what changed, why, and validation evidence.",
            "",
            "Required validation commands:",
            "- `git status --short`",
            "- `git diff --stat`",
            "- `npm test --silent || pytest -q || python -m pytest -q`",
            "- `python3 /home/daytona/quick_scan.py /home/daytona/repo > /home/daytona/agent_post_scan.json || true`",
            "",
            "Task queue (execute in order):",
        ]

        if not actionable_findings:
            lines.extend(
                [
                    "1) No actionable findings were detected in this scan.",
                    "2) Verify the project test suite still passes.",
                    "3) Return a brief validation summary.",
                ]
            )
        else:
            for idx, finding in enumerate(actionable_findings[:8], start=1):
                lines.append(
                    f"{idx}) {finding.check_id} [{finding.severity.upper()} / {finding.status.upper()}] - {finding.title}"
                )
                lines.append(f"   Why it matters: {self._business_impact_for_finding(finding)}")
                lines.append(f"   Evidence: {self._format_evidence(finding)}")
                if idx <= len(execution_plan):
                    plan_item = execution_plan[idx - 1]
                    lines.append(f"   Steps: {plan_item.get('steps')}")
                    lines.append(f"   Verification: {plan_item.get('verification')}")
                    lines.append(f"   Time estimate: {plan_item.get('estimate')}")
                lines.append("")

        lines.extend(
            [
                "Final response format:",
                "Return STRICT JSON only with this schema:",
                "{",
                '  "status": "done" | "blocked",',
                '  "summary": "technical summary",',
                '  "user_summary": "plain-English update for the user",',
                '  "assumptions": ["assumption 1"],',
                '  "asked_follow_up_questions": false,',
                '  "branch_name": "actual branch name",',
                '  "implementation_doc": "docs/agent-implementation-note.md",',
                '  "files_changed": ["path/to/file"],',
                '  "tests": {"command": "command used", "passed": true, "notes": "short evidence"},',
                '  "scan": {"actionable_before": 0, "actionable_after": 0, "top_remaining": ["CHECK_ID"]},',
                '  "risks": ["risk 1"],',
                '  "follow_up_prs": ["optional follow-up"]',
                "}",
                "```",
                "",
                f"- Scan id: `{run_details.get('scan_id', 'unknown')}`",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def _slug_for_branch(value: str, max_len: int) -> str:
        safe_chars: list[str] = []
        for ch in str(value).lower():
            if ch.isalnum():
                safe_chars.append(ch)
            elif ch in {" ", "-", "_", "/", "."}:
                safe_chars.append("-")
        compact = "".join(safe_chars).strip("-")
        compact = "-".join([part for part in compact.split("-") if part])
        if not compact:
            compact = "run"
        return compact[:max_len].rstrip("-")

    @staticmethod
    def _default_model_for_provider(provider: str) -> str:
        return {
            "openai": "openai/gpt-5.2-codex",
            "anthropic": "anthropic/claude-sonnet-4.5",
            "google": "google/gemini-2.5-pro",
        }.get(provider, "openai/gpt-5.2-codex")

    @staticmethod
    def _provider_packet_overlay(provider: str, model: str) -> list[str]:
        base = [f"Use `{model}` and optimize for deterministic, executable output."]
        if provider == "openai":
            base.extend(
                [
                    "Front-load constraints and output schema exactly; do not drift from requested format.",
                    "Prefer explicit command execution and short evidence-backed summaries.",
                ]
            )
        elif provider == "anthropic":
            base.extend(
                [
                    "Be clear and direct; keep reasoning concise and action-first.",
                    "Use structured sections internally but return only the requested final JSON.",
                ]
            )
        elif provider == "google":
            base.extend(
                [
                    "Follow deterministic system-instruction behavior with strict schema fidelity.",
                    "Resolve ambiguity with explicit assumptions and continue execution.",
                ]
            )
        else:
            base.append("Use concise execution-first behavior and strict output compliance.")
        return base

    def _compose_report_pdf_base64(
        self,
        *,
        intake_context: dict,
        score_summary: dict,
        strengths: list[str],
        actionable_findings: list[Tier1Finding],
        execution_plan: list[dict],
        launch_guidance: dict,
        run_details: dict,
    ) -> str | None:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception:
            return None

        page_w, page_h = 1240, 1754
        margin = 72
        pages: list = []
        font = ImageFont.load_default()

        def _new_page():
            page = Image.new("RGB", (page_w, page_h), "white")
            draw = ImageDraw.Draw(page)
            return page, draw, margin

        page, draw, y = _new_page()

        def _append_page(current_page):
            pages.append(current_page)

        def _line_height() -> int:
            return 22

        def _text_width(text: str) -> int:
            box = draw.textbbox((0, 0), text, font=font)
            return int(box[2] - box[0])

        def _ensure_space(height: int):
            nonlocal page, draw, y
            if y + height <= page_h - margin:
                return
            _append_page(page)
            page, draw, y = _new_page()

        def _write_wrapped(text: str, *, indent: int = 0):
            nonlocal y
            max_w = page_w - margin - (margin + indent)
            words = text.split()
            if not words:
                y += _line_height()
                return
            current = words[0]
            for word in words[1:]:
                candidate = f"{current} {word}"
                if _text_width(candidate) <= max_w:
                    current = candidate
                else:
                    _ensure_space(_line_height())
                    draw.text((margin + indent, y), current, fill="black", font=font)
                    y += _line_height()
                    current = word
            _ensure_space(_line_height())
            draw.text((margin + indent, y), current, fill="black", font=font)
            y += _line_height()

        def _write_heading(text: str):
            nonlocal y
            _ensure_space(34)
            draw.text((margin, y), text, fill="black", font=font)
            y += 30

        product_summary = intake_context.get("product_summary", "Unknown project")
        target_users = intake_context.get("target_users", "Unknown users")

        _write_heading(f"Clarity Check Report: {product_summary}")
        _write_wrapped(f"Audience: {target_users}")
        _write_wrapped(f"Launch recommendation: {launch_guidance.get('decision')} - {launch_guidance.get('reason')}")
        _write_wrapped(
            f"Scores: health={score_summary.get('health_score', 0)}, security={score_summary.get('security_score', 0)}, reliability={score_summary.get('reliability_score', 0)}, scalability={score_summary.get('scalability_score', 0)}"
        )
        y += 8

        score_chart = self._score_profile_png_image(score_summary)
        if score_chart is not None:
            max_chart_w = page_w - (margin * 2)
            chart = score_chart.copy().resize((max_chart_w, int(score_chart.height * (max_chart_w / score_chart.width))))
            _ensure_space(chart.height + 12)
            page.paste(chart, (margin, y))
            y += chart.height + 12

        severity_chart = self._severity_profile_png_image(actionable_findings)
        if severity_chart is not None:
            max_chart_w = page_w - (margin * 2)
            chart = severity_chart.copy().resize((max_chart_w, int(severity_chart.height * (max_chart_w / severity_chart.width))))
            _ensure_space(chart.height + 18)
            page.paste(chart, (margin, y))
            y += chart.height + 18

        _write_heading("What is working well")
        if strengths:
            for item in strengths[:6]:
                _write_wrapped(f"- {item}", indent=12)
        else:
            _write_wrapped("- Core quality checks are currently stable.", indent=12)

        _write_heading("Top findings")
        if not actionable_findings:
            _write_wrapped("- No warnings or failures were detected.", indent=12)
        else:
            for idx, finding in enumerate(actionable_findings[:8], start=1):
                _write_wrapped(
                    f"{idx}. {finding.check_id} ({finding.severity.upper()} / {finding.status.upper()}): {finding.title}"
                )
                _write_wrapped(f"   Impact: {self._business_impact_for_finding(finding)}")
                _write_wrapped(f"   Evidence: {self._format_evidence(finding)}")

        _write_heading("Execution plan summary")
        for idx, item in enumerate(execution_plan[:5], start=1):
            _write_wrapped(f"{idx}. {item.get('title')} - {item.get('estimate')}")
            _write_wrapped(f"   {item.get('objective')}")

        _write_heading("Run details")
        _write_wrapped(f"Scan id: {run_details.get('scan_id', 'unknown')}")
        _write_wrapped(f"Repo sha: {run_details.get('repo_sha', 'unknown')}")
        _write_wrapped(
            f"Timings (ms): index={run_details.get('index_ms', 0)}, scan={run_details.get('scan_ms', 0)}, report={run_details.get('report_ms', 0)}, total={run_details.get('total_ms', 0)}"
        )
        usage = run_details.get("model_usage") or {}
        _write_wrapped(
            f"Model tokens: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
        )

        _append_page(page)

        pdf_buf = BytesIO()
        first = pages[0]
        rest = pages[1:]
        first.save(pdf_buf, format="PDF", save_all=True, append_images=rest, resolution=150.0)
        return base64.b64encode(pdf_buf.getvalue()).decode("ascii")

    @staticmethod
    def _finding_priority_key(finding: Tier1Finding) -> tuple[int, int]:
        status_rank = {"fail": 0, "warn": 1}.get(finding.status, 2)
        severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(finding.severity, 4)
        return (status_rank, severity_rank)

    @staticmethod
    def _top_risk_area(findings: list[Tier1Finding]) -> str:
        if not findings:
            return "none"
        counts: dict[str, int] = {}
        for finding in findings:
            counts[finding.category] = counts.get(finding.category, 0) + 1
        top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[0][0]
        return top

    @staticmethod
    def _business_impact_for_finding(finding: Tier1Finding) -> str:
        mapping = {
            "REL_001": "Bugs reach production more easily because core behavior is not protected by tests.",
            "REL_002": "Broken changes can merge unnoticed, which increases firefighting and rollback risk.",
            "REL_003": "Builds can drift across machines, causing inconsistent releases and slower incident response.",
            "REL_004": "Onboarding and deploys become fragile because required runtime config is undocumented.",
            "REL_005": "Incidents take longer to debug when errors are weakly logged or swallowed.",
            "SEC_001": "Exposed secrets can lead to account takeover, data loss, and emergency key rotation.",
            "SEC_002": "Leaked private keys can allow unauthorized access and force broad credential rotation.",
            "SEC_003": "Committing real env files can expose sensitive credentials to anyone with repo access.",
            "SEC_004": "Overly permissive CORS can allow untrusted origins to call sensitive endpoints.",
            "SEC_005": "Dynamic execution can turn malformed input into code execution vulnerabilities.",
            "SEC_006": "SQL injection paths can allow data exfiltration, corruption, or auth bypass.",
            "SEC_007": "Missing auth guards can expose endpoints to unauthorized users.",
            "SCL_001": "Oversized files slow reviews, increase merge conflicts, and raise change-failure risk.",
            "SCL_002": "Blocking calls reduce throughput and increase latency during traffic spikes.",
            "SCL_003": "Missing rate limits increases abuse risk and can degrade service during bursts.",
        }
        return mapping.get(
            finding.check_id,
            "This issue increases delivery risk and should be fixed before high-impact feature work.",
        )

    @staticmethod
    def _format_evidence(finding: Tier1Finding) -> str:
        if not finding.evidence:
            return "No file-level evidence captured."
        ev = finding.evidence[0]
        if ev.line_number:
            return f"`{ev.file_path}:{ev.line_number}`"
        if ev.snippet:
            return f"`{ev.file_path}` ({ev.snippet})"
        return f"`{ev.file_path}`"

    @staticmethod
    def _launch_recommendation(findings: list[Tier1Finding], shipping_posture: str) -> dict:
        if not findings:
            return {"decision": "Proceed", "reason": "No blocking issues were found."}

        has_security_fail = any(
            f.category == "security" and f.status == "fail" and f.severity in {"high", "critical"}
            for f in findings
        )
        high_fails = [
            f for f in findings if f.status == "fail" and f.severity in {"high", "critical"}
        ]

        if has_security_fail:
            return {
                "decision": "Delay launch",
                "reason": "A high-severity security failure is present. Fix before exposing production traffic.",
            }
        if len(high_fails) >= 2:
            return {
                "decision": "Delay launch",
                "reason": "Multiple high-severity failures increase rollback risk. Resolve top failures before release.",
            }
        if high_fails:
            return {
                "decision": "Proceed with mitigation",
                "reason": "One high-severity failure exists. Ship only with owner assignment and an immediate fix window.",
            }

        if shipping_posture == "production_first":
            return {
                "decision": "Proceed with mitigation",
                "reason": "No hard blockers, but close remaining warnings before broad rollout.",
            }
        return {
            "decision": "Proceed",
            "reason": "No launch-blocking failures detected; track warnings in the next sprint.",
        }

    @staticmethod
    def _compose_risk_narrative(
        *,
        findings: list[Tier1Finding],
        target_users: str,
        launch_guidance: dict,
    ) -> str:
        if not findings:
            return "No compounding risk pattern was detected in this run."

        top = findings[0]
        primary_impact = Tier1Reporter._business_impact_for_finding(top)
        narrative = f"Primary risk: {primary_impact} Likely blast radius is degraded reliability for {target_users}."

        if len(findings) >= 2:
            second = findings[1]
            secondary_impact = Tier1Reporter._business_impact_for_finding(second).lower()
            narrative += f" It compounds with a second issue ({secondary_impact}), increasing release incident risk."

        narrative += f" Launch call: **{launch_guidance.get('decision')}**."
        return narrative

    def _build_strengths(
        self,
        findings: list[Tier1Finding],
        score_summary: dict,
        index_facts: dict,
        git_metadata: dict,
    ) -> list[str]:
        strengths: list[str] = []

        if score_summary.get("security_score", 0) >= 90:
            strengths.append("No critical security issues were detected in this run.")
        if score_summary.get("scalability_score", 0) >= 90:
            strengths.append("No major performance bottlenecks were detected in request paths.")
        if index_facts.get("has_tests"):
            strengths.append("Automated tests are present, which reduces regression risk.")
        if index_facts.get("has_ci"):
            strengths.append("CI workflows are present, so checks can run before merge.")
        if index_facts.get("lockfiles_present"):
            strengths.append("Dependency lockfiles are committed for repeatable installs.")

        sec_problem_ids = {"SEC_001", "SEC_002", "SEC_003", "SEC_004", "SEC_005", "SEC_006", "SEC_007"}
        sec_failures = [
            f for f in findings
            if f.check_id in sec_problem_ids and f.status in {"warn", "fail"}
        ]
        if not sec_failures:
            strengths.append("No hardcoded secrets, private keys, or obvious injection-risk patterns were detected.")

        if git_metadata.get("history_available") and int(git_metadata.get("contributors_90d", 0)) >= 2:
            strengths.append(
                f"The repo has active collaboration ({git_metadata.get('contributors_90d')} contributors recently)."
            )

        return strengths[:6]

    def _build_execution_plan(self, findings: list[Tier1Finding], git_metadata: dict) -> list[dict]:
        plan: list[dict] = []
        for finding in findings[:8]:
            hotspot_context = self._hotspot_context_for_finding(finding, git_metadata)
            plan.append(
                {
                    "title": f"{finding.check_id} {finding.title}",
                    "objective": self._objective_for_finding(finding),
                    "estimate": self._estimate_for_finding(finding),
                    "deliverables": self._deliverables_for_finding(finding),
                    "steps": self._steps_for_finding(finding),
                    "verification": self._verification_for_finding(finding),
                    "agent_prompt": self._agent_prompt_for_finding(finding, hotspot_context),
                }
            )
        return plan

    @staticmethod
    def _objective_for_finding(finding: Tier1Finding) -> str:
        mapping = {
            "REL_001": "Create baseline automated coverage for core user journeys.",
            "REL_002": "Establish CI automation for lint, test, and build checks.",
            "REL_003": "Ensure deterministic dependency resolution in all environments.",
            "REL_004": "Document runtime configuration contract in .env.example.",
            "SEC_001": "Eliminate hardcoded secrets and rotate compromised keys.",
            "SEC_002": "Remove committed private key material and rotate credentials.",
            "SEC_004": "Constrain CORS to trusted origins with safe credential policy.",
            "SEC_006": "Replace query interpolation with parameterized statements.",
        }
        return mapping.get(finding.check_id, "Reduce risk associated with this finding and codify the fix in tests/CI.")

    @staticmethod
    def _steps_for_finding(finding: Tier1Finding) -> str:
        default = (
            "1) Reproduce and localize the issue. "
            "2) Implement a minimal fix in the affected module. "
            "3) Add or update tests for regression protection. "
            "4) Document the change in PR notes."
        )
        mapping = {
            "REL_001": "1) Add a tests/ directory with smoke tests for key flows. 2) Introduce test runner config and scripts. 3) Add assertions for core business paths. 4) Wire tests into CI.",
            "REL_002": "1) Add `.github/workflows/ci.yml`. 2) Run install, lint, test, build jobs. 3) Enforce PR status checks. 4) Add badge/docs for contributors.",
            "REL_003": "1) Generate lockfile with your package manager. 2) Commit lockfile. 3) Use frozen/locked install mode in CI. 4) Validate deterministic install on fresh clone.",
            "REL_004": "1) Enumerate env vars used in code. 2) Add `.env.example` placeholders and comments. 3) Fail fast on missing required vars. 4) Add onboarding docs for local setup.",
            "SEC_001": "1) Remove hardcoded secret literals. 2) Load from environment or secret manager. 3) Rotate exposed tokens. 4) Add secret scanning in CI.",
            "SEC_002": "1) Delete committed key files and purge history if necessary. 2) Rotate impacted keys. 3) Store keys securely outside repo. 4) Add pre-commit and CI secret checks.",
            "SEC_004": "1) Replace wildcard CORS origins with explicit allowlist. 2) Disable credentials unless strictly needed. 3) Add tests for allowed/blocked origins. 4) Review prod config parity.",
            "SEC_006": "1) Find string-built SQL queries. 2) Replace with parameterized query APIs. 3) Add tests for malicious payload attempts. 4) Run static checks for risky patterns.",
        }
        return mapping.get(finding.check_id, default)

    @staticmethod
    def _verification_for_finding(finding: Tier1Finding) -> str:
        return (
            "1) Re-run Tier 1 scan and confirm this check improves. "
            "2) Run lint/tests and confirm green status. "
            "3) Add a short PR note with before/after evidence."
        )

    @staticmethod
    def _agent_prompt_for_finding(finding: Tier1Finding, hotspot_context: str | None) -> str:
        hotspot = f" Hotspot context: {hotspot_context}." if hotspot_context else ""
        return (
            f"Fix {finding.check_id} ({finding.title}). "
            "Limit scope to files tied to this finding. "
            "Follow the listed steps exactly, run lint/tests, and include before/after proof in your summary."
            f"{hotspot}"
        )

    @staticmethod
    def _estimate_for_finding(finding: Tier1Finding) -> str:
        mapping = {
            "SEC_001": "2-4 hours",
            "SEC_002": "2-6 hours",
            "SEC_004": "1-3 hours",
            "SEC_006": "2-5 hours",
            "REL_001": "4-8 hours",
            "REL_002": "1-3 hours",
            "REL_003": "1-2 hours",
            "REL_004": "30-90 minutes",
            "SCL_001": "2-6 hours",
            "SCL_002": "2-5 hours",
            "SCL_003": "1-3 hours",
        }
        return mapping.get(finding.check_id, "1-3 hours")

    @staticmethod
    def _deliverables_for_finding(finding: Tier1Finding) -> str:
        mapping = {
            "REL_004": "`.env.example` added/updated, required vars documented, startup validation added.",
            "REL_002": "CI workflow file committed and required checks enabled.",
            "REL_001": "New tests for critical flows plus passing test command.",
            "SCL_001": "Large source file reduced or split, with tests proving unchanged behavior.",
            "SEC_001": "Secrets removed, rotation completed, and scanning guardrail added.",
        }
        return mapping.get(
            finding.check_id,
            "Code changes merged with test evidence and short rollback plan.",
        )

    @staticmethod
    def _hotspot_context_for_finding(finding: Tier1Finding, git_metadata: dict) -> str | None:
        churn_rows = list(git_metadata.get("top_churn_files_90d") or [])
        if not churn_rows or not finding.evidence:
            return None

        churn_paths = {str(row.get("file_path")) for row in churn_rows if row.get("file_path")}
        finding_paths = {ev.file_path for ev in finding.evidence if ev.file_path}
        overlap = sorted(churn_paths.intersection(finding_paths))
        if not overlap:
            return None
        return f"frequently changed files involved: {', '.join(overlap[:3])}"

    @staticmethod
    def _default_educational_guidance(
        findings: list[Tier1Finding],
        explanation_style: str,
        technical_level: str,
    ) -> list[str]:
        if not findings:
            return [
                "- Keep preventive controls ahead of feature work: tests, CI checks, and secret scanning.",
            ]

        lines: list[str] = []
        for finding in findings[:3]:
            lesson = {
                "REL_004": "Document environment variables in `.env.example` so setup errors happen in development, not during deploy.",
                "REL_002": "Use CI as a merge gate to catch failures before they reach main.",
                "REL_001": "Protect core user flows with automated tests to prevent repeat regressions.",
                "SCL_001": "Large files are change-risk magnets; split by responsibility to speed reviews and reduce conflicts.",
                "SCL_002": "Move blocking work off request paths to keep latency stable under load.",
                "SEC_001": "Treat secret leaks as incident response: remove, rotate, and add prevention in CI.",
                "SEC_006": "Parameterized queries are non-negotiable when user input touches data access.",
            }.get(
                finding.check_id,
                "Add a guardrail (test, lint rule, or policy) so this class of issue stays fixed.",
            )
            lines.append(f"- `{finding.check_id}`: {lesson}")

        if explanation_style == "teach_me":
            lines.append("- Learning loop: identify the failure mode, ship one guardrail, then prove it with a test.")
        elif explanation_style == "cto_brief":
            lines.append("- Prioritize fixes by customer impact and rollback cost, not by code elegance.")
        else:
            lines.append("- Execute high-severity fixes first, then close medium-risk hygiene debt.")

        if explanation_style != "teach_me":
            if technical_level == "founder":
                lines.append("- These fixes reduce release anxiety and protect team velocity.")
            elif technical_level == "vibe_coder":
                lines.append("- Fast iteration is safe only when tests and CI are strict.")

        return lines

    @staticmethod
    def _style_guide(user_preferences: dict | None) -> dict:
        prefs = user_preferences or {}
        explanation_style = prefs.get("explanation_style") or "just_steps"
        technical_level = prefs.get("technical_level") or "engineer"
        shipping_posture = prefs.get("shipping_posture") or "balanced"

        style_hint = {
            "teach_me": "Explain reasoning briefly and include one educational takeaway per major finding.",
            "just_steps": "Use concise direct instructions and avoid long theory.",
            "cto_brief": "Use executive tone, emphasize risk, sequencing, and impact.",
        }.get(explanation_style, "Use concise direct instructions.")

        return {
            "technical_level": technical_level,
            "explanation_style": explanation_style,
            "shipping_posture": shipping_posture,
            "style_hint": style_hint,
        }

    def _finalize_run_details(
        self,
        *,
        run_details: dict,
        report_ms: int,
        model_usage: dict | None,
    ) -> dict:
        total_before_report_ms = int(run_details.get("total_before_report_ms") or 0)
        total_ms = total_before_report_ms + report_ms

        usage = self._normalized_usage(model_usage)
        compute_usd = self._estimate_compute_cost_usd(total_ms)
        llm_usd = self._estimate_llm_cost_usd(usage)

        return {
            **run_details,
            "report_ms": report_ms,
            "total_ms": total_ms,
            "cost_breakdown": {
                "compute_usd": round(compute_usd, 6),
                "llm_usd": round(llm_usd, 6),
                "total_usd": round(compute_usd + llm_usd, 6),
                "assumptions": {
                    "sandbox_cpu": settings.sandbox_cpu,
                    "sandbox_memory_gb": settings.sandbox_memory_gb,
                    "daytona_vcpu_per_sec_usd": DAYTONA_VCPU_PER_SEC_USD,
                    "daytona_ram_gb_per_sec_usd": DAYTONA_RAM_GB_PER_SEC_USD,
                    "llm_prompt_per_million_usd": LLM_INPUT_PER_MILLION_USD,
                    "llm_completion_per_million_usd": LLM_OUTPUT_PER_MILLION_USD,
                },
            },
            "model_usage": usage,
        }

    @staticmethod
    def _normalized_usage(model_usage: dict | None) -> dict:
        if not isinstance(model_usage, dict):
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        prompt_tokens = int(model_usage.get("prompt_tokens") or 0)
        completion_tokens = int(model_usage.get("completion_tokens") or 0)
        total_tokens = int(model_usage.get("total_tokens") or (prompt_tokens + completion_tokens))
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    @staticmethod
    def _estimate_compute_cost_usd(total_ms: int) -> float:
        seconds = max(0.0, float(total_ms) / 1000.0)
        per_second = (
            (settings.sandbox_cpu * DAYTONA_VCPU_PER_SEC_USD)
            + (settings.sandbox_memory_gb * DAYTONA_RAM_GB_PER_SEC_USD)
        )
        return per_second * seconds

    @staticmethod
    def _estimate_llm_cost_usd(usage: dict) -> float:
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
        prompt_cost = (prompt_tokens / 1_000_000.0) * LLM_INPUT_PER_MILLION_USD
        completion_cost = (completion_tokens / 1_000_000.0) * LLM_OUTPUT_PER_MILLION_USD
        return prompt_cost + completion_cost
