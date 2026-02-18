#!/usr/bin/env python3
"""Run Daytona sandbox tests + Tier 1 prompt/model matrix.

Outputs:
- doc/runs/daytona-matrix-<timestamp>.json
- doc/runs/daytona-matrix-<timestamp>.md
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import settings
from sandbox.manager import SandboxManager
from services.github import get_head_sha, get_repo_info, parse_repo_url
from tier1.indexer import DeterministicIndexer
from tier1.reporter import Tier1Reporter
from tier1.scanner import DeterministicScanner


ROOT_DIR = BACKEND_DIR.parent
RUNS_DIR = ROOT_DIR / "doc" / "runs"


@dataclass(frozen=True)
class RepoTestTarget:
    label: str
    repo_url: str
    install_cmd: str
    test_cmd: str


@dataclass(frozen=True)
class PromptProfile:
    label: str
    technical_level: str
    explanation_style: str
    shipping_posture: str


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _tail(text: str, limit: int = 4000) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[-limit:]


def _slug(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in {"/", "-", ".", " "}:
            out.append("-")
    return "".join(out).strip("-")


def _summary_scores(findings: list) -> dict:
    penalties = {"critical": 18, "high": 10, "medium": 6, "low": 3}
    scores = {"security": 100, "reliability": 100, "scalability": 100}

    for finding in findings:
        if finding.status == "pass":
            continue
        penalty = penalties.get(finding.severity, 4)
        if finding.status == "warn":
            penalty = max(1, penalty // 2)
        scores[finding.category] = max(0, scores[finding.category] - penalty)

    health = round((scores["security"] + scores["reliability"] + scores["scalability"]) / 3)
    return {
        "health_score": int(health),
        "security_score": int(scores["security"]),
        "reliability_score": int(scores["reliability"]),
        "scalability_score": int(scores["scalability"]),
    }


def _find_launch_line(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("- Launch recommendation:"):
            return line.removeprefix("- Launch recommendation: ").strip()
    return None


def _best_combo(rows: list[dict]) -> dict | None:
    valid = [r for r in rows if not r.get("fallback_used")]
    if not valid:
        return None
    return min(
        valid,
        key=lambda r: (
            float(r.get("total_usd") or 999.0),
            int(r.get("total_ms") or 999_999),
            int(r.get("total_tokens") or 9_999_999),
        ),
    )


async def run_repo_test_in_daytona(target: RepoTestTarget) -> dict:
    mgr = SandboxManager()
    scan_id = uuid4()
    owner, repo = await parse_repo_url(target.repo_url)
    info = await get_repo_info(owner, repo, token=None)

    steps: list[dict] = []
    started = time.perf_counter()

    async def run_step(cmd: str, cwd: str = "/home/daytona/repo", timeout: int = 600) -> dict:
        step_start = time.perf_counter()
        result = await mgr.exec(scan_id, cmd, cwd=cwd, timeout=timeout)
        step = {
            "cmd": cmd,
            "cwd": cwd,
            "exit_code": int(result.exit_code),
            "duration_ms": int((time.perf_counter() - step_start) * 1000),
            "stdout_tail": _tail(result.stdout, 3500),
            "stderr_tail": _tail(result.stderr, 2000),
        }
        steps.append(step)
        return step

    try:
        await mgr.provision(scan_id, info.clone_url)
        await run_step("apt-get update -y", cwd="/home/daytona", timeout=300)
        await run_step("apt-get install -y git nodejs npm", cwd="/home/daytona", timeout=600)
        await run_step("node -v && npm -v && git --version", cwd="/home/daytona", timeout=60)
        install_step = await run_step(target.install_cmd)
        test_step = await run_step(target.test_cmd, timeout=1200)

        ok = install_step["exit_code"] == 0 and test_step["exit_code"] == 0
        reason = "tests_passed" if ok else "tests_failed_or_setup_failed"
    except Exception as exc:  # noqa: BLE001
        ok = False
        reason = "sandbox_error"
        steps.append(
            {
                "cmd": "<internal>",
                "cwd": None,
                "exit_code": -1,
                "duration_ms": 0,
                "stdout_tail": "",
                "stderr_tail": str(exc),
            }
        )
    finally:
        await mgr.destroy(scan_id)

    return {
        "label": target.label,
        "repo_url": target.repo_url,
        "ok": ok,
        "reason": reason,
        "duration_ms": int((time.perf_counter() - started) * 1000),
        "steps": steps,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def run_report_matrix(
    *,
    repo_url: str,
    models: list[str],
    prompt_profiles: list[PromptProfile],
) -> dict:
    owner, repo = await parse_repo_url(repo_url)
    info = await get_repo_info(owner, repo, token=None)
    repo_sha = await get_head_sha(owner, repo, info.default_branch, token=None)

    scan_id = uuid4()
    index_started = time.perf_counter()
    index_payload = await DeterministicIndexer().build_or_reuse(
        project_id=None,
        user_id=None,
        repo_url=repo_url,
        clone_url=info.clone_url,
        repo_sha=repo_sha,
        github_token=None,
        scan_id=scan_id,
    )
    index_ms = int((time.perf_counter() - index_started) * 1000)

    scan_started = time.perf_counter()
    findings = DeterministicScanner().scan(index_payload=index_payload, sensitive_data=[])
    scan_ms = int((time.perf_counter() - scan_started) * 1000)
    scores = _summary_scores(findings)
    actionable = [f for f in findings if f.status in {"warn", "fail"}]

    git_metadata = (index_payload.get("index_json") or {}).get("facts", {}).get("git_metadata") or {}
    index_facts = (index_payload.get("index_json") or {}).get("facts") or {}

    rows: list[dict] = []
    for model in models:
        for profile in prompt_profiles:
            settings.tier1_assistant_model = model
            reporter = Tier1Reporter()
            run_scan_id = str(uuid4())
            run_details = {
                "scan_id": run_scan_id,
                "repo_sha": repo_sha,
                "run_started_at": datetime.now(timezone.utc).isoformat(),
                "index_source": "fresh",
                "cache_hit": False,
                "file_count": int(index_payload.get("file_count") or 0),
                "loc_total": int(index_payload.get("loc_total") or 0),
                "index_generated_at": (index_payload.get("index_json") or {}).get("generated_at"),
                "index_ms": index_ms,
                "scan_ms": scan_ms,
                "checks_evaluated": len(findings),
                "total_before_report_ms": index_ms + scan_ms,
                "reports_generated_before": 0,
                "report_limit": settings.tier1_monthly_report_cap,
            }

            artifact = await reporter.generate_report(
                findings=findings,
                score_summary=scores,
                intake_context={
                    "product_summary": f"{owner}/{repo}",
                    "target_users": "Node.js backend teams",
                    "repo_url": repo_url,
                },
                user_preferences={
                    "technical_level": profile.technical_level,
                    "explanation_style": profile.explanation_style,
                    "shipping_posture": profile.shipping_posture,
                },
                run_details=run_details,
                git_metadata=git_metadata,
                index_facts=index_facts,
            )

            details = artifact.summary_json.get("run_details") or {}
            usage = details.get("model_usage") or {}
            costs = details.get("cost_breakdown") or {}

            model_slug = _slug(model)
            profile_slug = _slug(profile.label)
            base_name = f"daytona-matrix-{_slug(owner)}-{_slug(repo)}-{model_slug}-{profile_slug}-{_now_ts()}"
            md_path = RUNS_DIR / f"{base_name}.md"
            agent_path = RUNS_DIR / f"{base_name}.agent.md"
            md_path.write_text(artifact.markdown, encoding="utf-8")
            agent_path.write_text(artifact.agent_markdown, encoding="utf-8")

            row = {
                "model": model,
                "prompt_profile": profile.label,
                "technical_level": profile.technical_level,
                "explanation_style": profile.explanation_style,
                "shipping_posture": profile.shipping_posture,
                "fallback_used": bool(artifact.fallback_used),
                "total_ms": int(details.get("total_ms") or 0),
                "report_ms": int(details.get("report_ms") or 0),
                "total_tokens": int(usage.get("total_tokens") or 0),
                "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                "completion_tokens": int(usage.get("completion_tokens") or 0),
                "compute_usd": float(costs.get("compute_usd") or 0.0),
                "llm_usd": float(costs.get("llm_usd") or 0.0),
                "total_usd": float(costs.get("total_usd") or 0.0),
                "launch_recommendation": _find_launch_line(artifact.markdown),
                "report_markdown_path": str(md_path),
                "agent_markdown_path": str(agent_path),
                "report_sections": {
                    "has_strengths": "## What You're Doing Well" in artifact.markdown,
                    "has_findings": "## Top Findings" in artifact.markdown,
                    "has_education": "## Educational Guidance" in artifact.markdown,
                    "has_execution_plan": "## Coding Agent Execution Plan" in artifact.markdown,
                    "has_run_details": "## Run Details" in artifact.markdown,
                },
            }
            rows.append(row)

    return {
        "repo_url": repo_url,
        "repo_sha": repo_sha,
        "loc_total": int(index_payload.get("loc_total") or 0),
        "file_count": int(index_payload.get("file_count") or 0),
        "scores": scores,
        "actionable_findings_count": len(actionable),
        "actionable_findings": [
            {
                "check_id": f.check_id,
                "severity": f.severity,
                "status": f.status,
                "category": f.category,
                "title": f.title,
            }
            for f in actionable
        ],
        "matrix": rows,
        "best_combo": _best_combo(rows),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _write_summary_markdown(
    *,
    out_path: Path,
    payload: dict,
) -> None:
    lines: list[str] = [
        "# Daytona Prompt + Model Matrix",
        "",
        "## Scope",
        f"- Generated at: `{payload.get('generated_at')}`",
        "- Daytona sandboxes were used for repo test execution.",
        f"- Report matrix target repo: `{payload['report_matrix']['repo_url']}`",
        "",
        "## Repo Test Runs (Daytona)",
    ]

    for test in payload["daytona_tests"]:
        lines.extend(
            [
                f"- `{test['label']}` — `{test['repo_url']}`",
                f"  - Result: **{'pass' if test['ok'] else 'fail'}** (`{test['reason']}`)",
                f"  - Duration: `{test['duration_ms']} ms`",
                f"  - Steps: `{len(test['steps'])}`",
            ]
        )

    matrix = payload["report_matrix"]["matrix"]
    lines.extend(
        [
            "",
            "## Prompt/Model Matrix",
            "",
            "| Model | Prompt Profile | Fallback | Total ms | Tokens | Total USD |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in matrix:
        lines.append(
            f"| `{row['model']}` | `{row['prompt_profile']}` | `{row['fallback_used']}` | {row['total_ms']} | {row['total_tokens']} | {row['total_usd']:.6f} |"
        )

    best = payload["report_matrix"].get("best_combo")
    if best:
        lines.extend(
            [
                "",
                "## Recommended Default",
                f"- Model: `{best['model']}`",
                f"- Prompt profile: `{best['prompt_profile']}`",
                f"- Why: lowest cost/time among non-fallback runs in this matrix.",
                f"- Report: `{best['report_markdown_path']}`",
                f"- Agent packet: `{best['agent_markdown_path']}`",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Recommended Default",
                "- No non-fallback run found; keep current default model and investigate parser/response format handling.",
            ]
        )

    lines.extend(
        [
            "",
            "## Raw Artifact",
            f"- JSON: `{payload['json_path']}`",
        ]
    )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def main() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    ts = _now_ts()

    # Daytona repo test workload (parallel).
    repo_targets = [
        RepoTestTarget(
            label="express",
            repo_url="https://github.com/expressjs/express",
            install_cmd="npm install --silent",
            test_cmd="npm test --silent",
        ),
        RepoTestTarget(
            label="uuid",
            repo_url="https://github.com/uuidjs/uuid",
            install_cmd="npm install --silent",
            test_cmd="npm test --silent",
        ),
    ]
    daytona_results = await asyncio.gather(*(run_repo_test_in_daytona(t) for t in repo_targets))

    # Prompt + model matrix for issue-heavy repo.
    models = [
        "openai/gpt-5.2-chat",
        "anthropic/claude-sonnet-4.5",
        "x-ai/grok-4-fast",
    ]
    prompt_profiles = [
        PromptProfile(
            label="founder-teach-production-first",
            technical_level="founder",
            explanation_style="teach_me",
            shipping_posture="production_first",
        ),
        PromptProfile(
            label="engineer-just-steps-balanced",
            technical_level="engineer",
            explanation_style="just_steps",
            shipping_posture="balanced",
        ),
    ]
    report_matrix = await run_report_matrix(
        repo_url="https://github.com/expressjs/express",
        models=models,
        prompt_profiles=prompt_profiles,
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "daytona_tests": daytona_results,
        "report_matrix": report_matrix,
    }

    json_path = RUNS_DIR / f"daytona-matrix-{ts}.json"
    md_path = RUNS_DIR / f"daytona-matrix-{ts}.md"
    payload["json_path"] = str(json_path)

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_summary_markdown(out_path=md_path, payload=payload)

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    asyncio.run(main())
