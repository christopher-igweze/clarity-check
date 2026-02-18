#!/usr/bin/env python3
"""Run one-prompt OpenHands fix attempts fully inside Daytona sandboxes.

This script is intentionally sandbox-first:
- Repo clone, dependency install, tests, scans, and OpenHands execution happen in Daytona.
- Local machine only orchestrates Daytona API calls and writes result artifacts.

Outputs:
- doc/runs/daytona-openhands-matrix-<timestamp>.json
- doc/runs/daytona-openhands-matrix-<timestamp>.md
- doc/prompt-guides/ONE_SHOT_MATRIX_RESULTS.md
"""

from __future__ import annotations

import asyncio
import argparse
import concurrent.futures
import json
import math
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import settings
from sandbox.manager import SandboxManager
from services.github import get_repo_info, parse_repo_url


ROOT_DIR = BACKEND_DIR.parent
RUNS_DIR = ROOT_DIR / "doc" / "runs"

# Keep aligned with backend/tier1/reporter.py assumptions for apples-to-apples reporting.
DAYTONA_VCPU_PER_SEC_USD = 0.000014
DAYTONA_RAM_GB_PER_SEC_USD = 0.0000045
LLM_INPUT_PER_MILLION_USD = 0.10
LLM_OUTPUT_PER_MILLION_USD = 0.40

# Fit more parallel sandboxes under org quota for matrix runs.
MATRIX_SANDBOX_CPU = 1
MATRIX_SANDBOX_MEMORY_GB = 1
MATRIX_SANDBOX_DISK_GB = 3


LOCAL_SCAN_SCRIPT = r"""#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

LOCKFILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "poetry.lock",
    "pipfile.lock",
    "cargo.lock",
}

SECRET_PATTERNS = [
    ("sk_live", re.compile(r"sk_live_[A-Za-z0-9]+")),
    ("sk_test", re.compile(r"sk_test_[A-Za-z0-9]+")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack_bot", re.compile(r"xoxb-[0-9A-Za-z-]+")),
    ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
]

ENV_USAGE_PATTERN = re.compile(r"(process\.env\.[A-Z0-9_]+|os\.getenv\(|os\.environ\[|import\.meta\.env\.)")
SYNC_BLOCKING_PATTERN = re.compile(r"\b(fs\.[A-Za-z]+Sync\s*\(|subprocess\.(run|call|check_output)\s*\(|requests\.(get|post|put|delete)\s*\()", re.IGNORECASE)


def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except Exception:
        return None
    if b"\x00" in raw:
        return None
    if len(raw) > 1_500_000:
        raw = raw[:1_500_000]
    return raw.decode("utf-8", errors="replace")


def loc_count(content: str) -> int:
    return sum(1 for line in content.splitlines() if line.strip())


def add_finding(findings, check_id, title, category, severity, status, evidence):
    findings.append(
        {
            "check_id": check_id,
            "title": title,
            "category": category,
            "severity": severity,
            "status": status,
            "evidence_count": len(evidence),
            "evidence": evidence[:5],
        }
    )


def score_summary(findings):
    penalties = {"critical": 18, "high": 10, "medium": 6, "low": 3}
    scores = {"security": 100, "reliability": 100, "scalability": 100}
    for f in findings:
        if f["status"] == "pass":
            continue
        penalty = penalties.get(f["severity"], 4)
        if f["status"] == "warn":
            penalty = max(1, penalty // 2)
        scores[f["category"]] = max(0, scores[f["category"]] - penalty)
    health = round((scores["security"] + scores["reliability"] + scores["scalability"]) / 3)
    actionable = [f for f in findings if f["status"] in {"warn", "fail"}]
    return {
        "health_score": int(health),
        "security_score": int(scores["security"]),
        "reliability_score": int(scores["reliability"]),
        "scalability_score": int(scores["scalability"]),
        "actionable_count": len(actionable),
        "actionable_by_severity": dict(Counter(f["severity"] for f in actionable)),
    }


def collect_git_meta(repo: Path):
    out = {
        "commit_count_90d": 0,
        "top_authors_all_time": [],
        "hot_files_180d": [],
    }
    rc, stdout, _ = run(["git", "log", "--since=90.days", "--pretty=format:%H"], repo)
    if rc == 0 and stdout.strip():
        out["commit_count_90d"] = len([x for x in stdout.splitlines() if x.strip()])

    rc, stdout, _ = run(["git", "shortlog", "-sn", "--all"], repo)
    if rc == 0:
        rows = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) == 2 and parts[0].strip().isdigit():
                rows.append({"name": parts[1].strip(), "commits": int(parts[0].strip())})
            else:
                toks = line.split(" ", 1)
                if len(toks) == 2 and toks[0].isdigit():
                    rows.append({"name": toks[1].strip(), "commits": int(toks[0])})
        out["top_authors_all_time"] = rows[:5]

    rc, stdout, _ = run(["git", "log", "--since=180.days", "--name-only", "--pretty=format:"], repo)
    if rc == 0:
        counter = Counter()
        for line in stdout.splitlines():
            p = line.strip()
            if p:
                counter[p] += 1
        out["hot_files_180d"] = [{"path": k, "touches": v} for k, v in counter.most_common(8)]
    return out


def main():
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    rc, stdout, stderr = run(["git", "ls-files"], repo)
    if rc != 0:
        print(json.dumps({"error": "git ls-files failed", "stderr": stderr[-800:]}))
        raise SystemExit(2)

    files = [line.strip() for line in stdout.splitlines() if line.strip()]
    findings = []
    indexed = []
    loc_total = 0
    has_ci = False
    has_tests = False
    has_env_example = False
    tracked_env_files = []
    manifests_present = set()
    lockfiles_present = set()
    secret_hits = []
    env_usage_hits = []
    sync_hits = []

    for rel in files:
        lower = rel.lower()
        if lower.startswith(".github/workflows/"):
            has_ci = True
        if (
            "/test" in lower
            or "/tests" in lower
            or "__tests__" in lower
            or lower.endswith(".spec.ts")
            or lower.endswith(".spec.tsx")
            or lower.endswith(".spec.js")
            or lower.endswith(".spec.jsx")
            or lower.endswith("_test.py")
            or lower.endswith("test_.py")
        ):
            has_tests = True
        if lower in {".env.example", ".env.sample", ".env.template"}:
            has_env_example = True
        name = Path(lower).name
        if name.startswith(".env") and name not in {".env.example", ".env.sample", ".env.template"}:
            tracked_env_files.append(rel)
        if name in {"package.json", "requirements.txt", "pyproject.toml", "pom.xml", "go.mod", "cargo.toml"}:
            manifests_present.add(name)
        if name in LOCKFILE_NAMES:
            lockfiles_present.add(name)

        abs_path = repo / rel
        text = read_text(abs_path)
        if text is None:
            continue

        loc = loc_count(text)
        loc_total += loc
        indexed.append({"path": rel, "loc": loc})

        for label, pat in SECRET_PATTERNS:
            for m in pat.finditer(text):
                secret_hits.append({"file_path": rel, "match": label, "snippet": text[max(0, m.start()-40):m.end()+40]})
                if len(secret_hits) >= 20:
                    break
            if len(secret_hits) >= 20:
                break

        for m in ENV_USAGE_PATTERN.finditer(text):
            env_usage_hits.append({"file_path": rel, "match": m.group(1), "line_number": text[:m.start()].count("\n") + 1})
            if len(env_usage_hits) >= 40:
                break

        for m in SYNC_BLOCKING_PATTERN.finditer(text):
            sync_hits.append({"file_path": rel, "match": m.group(1), "line_number": text[:m.start()].count("\n") + 1})
            if len(sync_hits) >= 40:
                break

    over_500 = [f for f in indexed if f["loc"] > 500 and Path(f["path"]).name not in LOCKFILE_NAMES]
    over_800 = [f for f in indexed if f["loc"] > 800 and Path(f["path"]).name not in LOCKFILE_NAMES]

    add_finding(findings, "SEC_001", "Hardcoded API keys/secrets", "security", "critical", "fail" if secret_hits else "pass", secret_hits)
    add_finding(
        findings,
        "SEC_003",
        "Secret-bearing env files committed",
        "security",
        "high",
        "fail" if tracked_env_files else "pass",
        [{"file_path": p, "match": "tracked_env_file"} for p in tracked_env_files],
    )
    add_finding(
        findings,
        "REL_001",
        "Missing automated tests",
        "reliability",
        "high",
        "pass" if has_tests else "fail",
        [] if has_tests else [{"file_path": "(repo)", "match": "missing_tests"}],
    )
    add_finding(
        findings,
        "REL_002",
        "Missing CI workflow",
        "reliability",
        "medium",
        "pass" if has_ci else "warn",
        [] if has_ci else [{"file_path": ".github/workflows", "match": "missing_ci"}],
    )
    missing_lockfile = bool(manifests_present and not lockfiles_present)
    add_finding(
        findings,
        "REL_003",
        "Missing lockfile for dependency reproducibility",
        "reliability",
        "medium",
        "warn" if missing_lockfile else "pass",
        [] if not missing_lockfile else [{"file_path": "(repo)", "match": "missing_lockfile"}],
    )
    missing_env_template = bool(env_usage_hits and not has_env_example)
    add_finding(
        findings,
        "REL_004",
        "Env vars used but no .env.example",
        "reliability",
        "medium",
        "warn" if missing_env_template else "pass",
        [] if not missing_env_template else env_usage_hits,
    )
    add_finding(
        findings,
        "SCL_001",
        "God file size threshold exceeded",
        "scalability",
        "high" if over_800 else "medium",
        "fail" if over_800 else ("warn" if over_500 else "pass"),
        sorted(over_500, key=lambda x: x["loc"], reverse=True),
    )
    add_finding(
        findings,
        "SCL_002",
        "Blocking sync operations in request paths",
        "scalability",
        "medium",
        "warn" if sync_hits else "pass",
        sync_hits,
    )

    payload = {
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "repo_path": str(repo),
        "file_count": len(indexed),
        "loc_total": loc_total,
        "summary": score_summary(findings),
        "findings": findings,
        "git_metadata": collect_git_meta(repo),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
"""


OPENHANDS_RUNNER = r"""#!/usr/bin/env python3
import argparse
import json
import time
import traceback
from pathlib import Path

from pydantic import SecretStr
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.terminal import TerminalTool
from openhands.tools.file_editor import FileEditorTool
from openhands.sdk.conversation.response_utils import get_agent_final_response


def _extract_usage(events):
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def consume_map(d):
        if not isinstance(d, dict):
            return
        p = d.get("prompt_tokens")
        if p is None:
            p = d.get("input_tokens")
        c = d.get("completion_tokens")
        if c is None:
            c = d.get("output_tokens")
        t = d.get("total_tokens")
        if isinstance(p, int):
            usage["prompt_tokens"] = max(usage["prompt_tokens"], p)
        if isinstance(c, int):
            usage["completion_tokens"] = max(usage["completion_tokens"], c)
        if isinstance(t, int):
            usage["total_tokens"] = max(usage["total_tokens"], t)

    for event in events or []:
        data = None
        if hasattr(event, "model_dump"):
            try:
                data = event.model_dump(mode="python")
            except Exception:
                data = None
        if data is None and hasattr(event, "__dict__"):
            data = dict(getattr(event, "__dict__", {}) or {})
        if not isinstance(data, dict):
            continue

        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                consume_map(item)
                for value in item.values():
                    if isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(item, list):
                for value in item:
                    if isinstance(value, (dict, list)):
                        stack.append(value)

    if usage["total_tokens"] <= 0:
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
    return usage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    started = time.time()
    output = {
        "ok": False,
        "model": args.model,
        "workspace": args.workspace,
        "prompt_chars": len(prompt),
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "duration_ms": 0,
        "error": None,
        "final_response": "",
        "final_response_json": None,
        "event_count": 0,
    }

    try:
        llm = LLM(
            model=args.model,
            api_key=SecretStr(args.api_key),
            base_url=args.base_url,
            max_output_tokens=4096,
        )
        agent = Agent(
            llm=llm,
            tools=[
                Tool(name=TerminalTool.name),
                Tool(name=FileEditorTool.name),
            ],
        )
        conv = Conversation(agent=agent, workspace=args.workspace)
        conv.send_message(prompt)
        conv.run()
        events = getattr(conv.state, "events", None) or []
        output["event_count"] = len(events)
        output["usage"] = _extract_usage(events)
        final_text = (get_agent_final_response(events) or "").strip()
        output["final_response"] = final_text
        try:
            output["final_response_json"] = json.loads(final_text)
        except Exception:
            output["final_response_json"] = None
        output["ok"] = True
    except Exception:
        output["ok"] = False
        output["error"] = traceback.format_exc(limit=20)
    finally:
        output["duration_ms"] = int((time.time() - started) * 1000)
        Path(args.out).write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(json.dumps({"ok": output["ok"], "duration_ms": output["duration_ms"], "usage": output["usage"]}))


if __name__ == "__main__":
    main()
"""


@dataclass(frozen=True)
class RepoTarget:
    label: str
    repo_url: str
    install_cmd: str
    test_cmd: str


@dataclass(frozen=True)
class ModelTarget:
    label: str
    model: str
    guide_path: str


FOLLOW_UP_PATTERNS = [
    re.compile(r"\b(can you|could you|please provide|need more info|clarify)\b", re.IGNORECASE),
    re.compile(r"\?$"),
]


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _tail(value: str, limit: int = 2400) -> str:
    if not value:
        return ""
    return value if len(value) <= limit else value[-limit:]


def _slug(value: str) -> str:
    out: list[str] = []
    for ch in str(value).lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in {"-", "/", ".", " ", "_"}:
            out.append("-")
    compact = "".join(out).strip("-")
    return "-".join([part for part in compact.split("-") if part])


def _find_actionable(scan_payload: dict) -> list[dict]:
    findings = scan_payload.get("findings") or []
    return [f for f in findings if f.get("status") in {"warn", "fail"}]


def _extract_command_line(value: str) -> str:
    stripped = (value or "").strip()
    if "\n" in stripped:
        return stripped.splitlines()[0]
    return stripped


def _calc_costs(total_ms: int, usage: dict) -> dict:
    seconds = max(0.0, float(total_ms) / 1000.0)
    per_second = (
        (settings.sandbox_cpu * DAYTONA_VCPU_PER_SEC_USD)
        + (settings.sandbox_memory_gb * DAYTONA_RAM_GB_PER_SEC_USD)
    )
    compute_usd = per_second * seconds

    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or 0)
    llm_usd = (
        (prompt_tokens / 1_000_000.0) * LLM_INPUT_PER_MILLION_USD
        + (completion_tokens / 1_000_000.0) * LLM_OUTPUT_PER_MILLION_USD
    )
    return {
        "compute_usd": round(compute_usd, 6),
        "llm_usd": round(llm_usd, 6),
        "total_usd": round(compute_usd + llm_usd, 6),
    }


def _baseline_findings_text(scan_payload: dict, limit: int = 8) -> str:
    actionable = _find_actionable(scan_payload)
    lines: list[str] = []
    for finding in actionable[:limit]:
        lines.append(
            f"- [{finding.get('severity')}/{finding.get('status')}] {finding.get('check_id')}: {finding.get('title')} (evidence={finding.get('evidence_count', 0)})"
        )
    if not lines:
        lines.append("- No actionable findings found in baseline scan.")
    return "\n".join(lines)


def _prompt_for_model(
    *,
    model: str,
    repo: RepoTarget,
    baseline_scan: dict,
) -> str:
    base_task = f"""You are working in /home/daytona/repo.

Goal:
- In one pass, reduce actionable scan findings while keeping the repo healthy.
- Preserve behavior and avoid broad refactors.

Baseline findings:
{_baseline_findings_text(baseline_scan)}

Required execution plan:
1. Inspect relevant files and choose the smallest safe edits to reduce the baseline warnings/failures.
2. Run install and tests:
   - Install: `{repo.install_cmd}`
   - Test: `{repo.test_cmd}`
3. Re-run post-fix scan:
   - `python3 /home/daytona/quick_scan.py /home/daytona/repo > /home/daytona/agent_post_scan.json`

Hard constraints:
- Do not ask follow-up questions; make safe assumptions and proceed.
- Do not disable tests or CI checks.
- Keep changes focused and minimal.
- Create and use branch `codex/{_slug(repo.label)}-fix-${{RUN_ID}}`.
- Create/update `docs/agent-implementation-note.md`.

Required validation commands:
- `git status --short`
- `git diff --stat`
- `{repo.test_cmd}`

Final response requirements:
- Return STRICT JSON only (no markdown).
- Schema:
  {{
    "status": "done" | "blocked",
    "summary": "technical summary",
    "user_summary": "plain-English user update",
    "assumptions": ["assumption1"],
    "asked_follow_up_questions": false,
    "branch_name": "codex/...",
    "implementation_doc": "docs/agent-implementation-note.md",
    "files_changed": ["path1", "path2"],
    "tests": {{
      "command": "{_extract_command_line(repo.test_cmd)}",
      "passed": true | false,
      "notes": "short result"
    }},
    "scan": {{
      "actionable_before": <int>,
      "actionable_after": <int>,
      "top_remaining": ["CHECK_ID", "CHECK_ID"]
    }},
    "risks": ["risk1", "risk2"],
    "follow_up_prs": ["optional"]
  }}
"""

    if model.startswith("anthropic/"):
        return f"""<role>Act as a precise senior software engineer.</role>
<task>
{base_task}
</task>
<quality_bar>
Be clear and direct. Prefer concrete file edits and verifiable outcomes over broad advice.
</quality_bar>
"""
    if model.startswith("openai/"):
        return f"""Role: senior software engineer.

Deliverable: execute the task exactly and return strict JSON.

{base_task}

Follow the instructions exactly; prioritize correctness over verbosity.
"""
    if model.startswith("google/"):
        return f"""System instruction: complete the repository remediation task with deterministic steps.

{base_task}

Think privately, then execute commands and edits. Return only the final JSON.
"""
    return base_task


def compute_resource_worker_cap(
    *,
    pool_cpu: int,
    pool_memory_gb: int,
    pool_storage_gb: int,
    sandbox_cpu: int,
    sandbox_memory_gb: int,
    sandbox_disk_gb: int,
) -> int:
    cpu_cap = pool_cpu // max(1, sandbox_cpu)
    memory_cap = pool_memory_gb // max(1, sandbox_memory_gb)
    storage_cap = pool_storage_gb // max(1, sandbox_disk_gb)
    return max(0, min(cpu_cap, memory_cap, storage_cap))


def detect_follow_up_question(final_response: str, final_response_json: dict | None) -> bool:
    if isinstance(final_response_json, dict):
        explicit = final_response_json.get("asked_follow_up_questions")
        if isinstance(explicit, bool):
            return explicit

    if "?" in (final_response or ""):
        return True
    for pat in FOLLOW_UP_PATTERNS:
        if pat.search(final_response or ""):
            return True
    return False


def _severity_counts(findings: list[dict]) -> dict[str, int]:
    out = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        sev = str(finding.get("severity") or "").lower()
        if sev in out:
            out[sev] += 1
    return out


def _score_scan_delta(before_actionable: int, after_actionable: int, before_sev: dict[str, int], after_sev: dict[str, int]) -> float:
    reduction_ratio = 0.0
    if before_actionable > 0:
        reduction_ratio = max(0.0, (before_actionable - after_actionable) / before_actionable)
    reduction_score = min(100.0, reduction_ratio * 100.0)

    before_weighted = (before_sev["critical"] * 2) + before_sev["high"]
    after_weighted = (after_sev["critical"] * 2) + after_sev["high"]
    if before_weighted <= 0:
        severity_score = 100.0 if after_weighted <= 0 else 0.0
    else:
        severity_score = max(0.0, min(100.0, ((before_weighted - after_weighted) / before_weighted) * 100.0))

    return round((0.7 * reduction_score) + (0.3 * severity_score), 2)


def score_run(
    *,
    before_actionable: int,
    after_actionable: int,
    baseline_tests_exit: int,
    post_tests_exit: int,
    before_findings: list[dict],
    after_findings: list[dict],
    final_response: str,
    final_response_json: dict | None,
    changed_files: list[str],
    score_target: float,
    active_branch: str,
    implementation_doc_exists: bool,
) -> dict:
    asked_follow_up = detect_follow_up_question(final_response, final_response_json)
    c1 = 0.0 if asked_follow_up else 100.0

    valid_json = isinstance(final_response_json, dict)
    tests_pass = post_tests_exit == 0
    intended_fix = (before_actionable - after_actionable) > 0 or bool(changed_files)
    c2 = round((35.0 if valid_json else 0.0) + (35.0 if tests_pass else 0.0) + (30.0 if intended_fix else 0.0), 2)

    before_sev = _severity_counts(before_findings)
    after_sev = _severity_counts(after_findings)
    no_new_high_critical = (after_sev["critical"] + after_sev["high"]) <= (before_sev["critical"] + before_sev["high"])
    no_test_regression = not (baseline_tests_exit == 0 and post_tests_exit != 0)
    bounded_scope = len(changed_files) <= 12
    c3 = round((40.0 if no_new_high_critical else 0.0) + (30.0 if no_test_regression else 0.0) + (30.0 if bounded_scope else 0.0), 2)

    c4 = _score_scan_delta(before_actionable, after_actionable, before_sev, after_sev)

    user_summary_present = isinstance(final_response_json, dict) and bool(str(final_response_json.get("user_summary") or "").strip())
    branch_json = str((final_response_json or {}).get("branch_name") or "").strip()
    branch_ok = active_branch.startswith("codex/") or branch_json.startswith("codex/")
    implementation_doc_ok = implementation_doc_exists and str((final_response_json or {}).get("implementation_doc") or "").strip() == "docs/agent-implementation-note.md"
    c5 = 100.0 if (branch_ok and implementation_doc_ok and user_summary_present) else 0.0

    total = round((0.25 * c1) + (0.25 * c2) + (0.20 * c3) + (0.20 * c4) + (0.10 * c5), 2)
    hard_gate_failed = c1 < 100.0 or c5 < 100.0
    passed = (not hard_gate_failed) and total >= score_target
    return {
        "criteria": {
            "c1_one_shot_compliance": c1,
            "c2_execution_quality": c2,
            "c3_regression_prevention": c3,
            "c4_scan_delta_quality": c4,
            "c5_delivery_discipline": c5,
        },
        "weighted_total": total,
        "hard_gate_failed": hard_gate_failed,
        "passed": passed,
        "checks": {
            "asked_follow_up": asked_follow_up,
            "valid_json": valid_json,
            "tests_pass_post_fix": tests_pass,
            "no_new_high_critical": no_new_high_critical,
            "no_test_regression": no_test_regression,
            "bounded_change_scope": bounded_scope,
            "branch_ok": branch_ok,
            "implementation_doc_ok": implementation_doc_ok,
            "user_summary_present": user_summary_present,
        },
    }


async def _preflight_repo(repo: RepoTarget) -> dict:
    mgr = SandboxManager()
    scan_id = uuid4()
    owner, name = await parse_repo_url(repo.repo_url)
    info = await get_repo_info(owner, name, token=None)
    steps: list[dict[str, Any]] = []
    started = time.perf_counter()

    async def run_step(cmd: str, cwd: str, timeout: int = 1200) -> dict[str, Any]:
        step_started = time.perf_counter()
        result = await mgr.exec(scan_id, cmd, cwd=cwd, timeout=timeout)
        row = {
            "cmd": cmd,
            "cwd": cwd,
            "exit_code": int(result.exit_code),
            "duration_ms": int((time.perf_counter() - step_started) * 1000),
            "stdout_tail": _tail(result.stdout, 4000),
        }
        steps.append(row)
        return row

    ok = False
    error = None
    try:
        await mgr.provision(scan_id, info.clone_url)
        setup = await run_step(
            "apt-get update -y && apt-get install -y git nodejs npm && "
            "python3 -m pip install --no-input --upgrade pip",
            cwd="/home/daytona",
            timeout=1800,
        )
        if setup["exit_code"] != 0:
            raise RuntimeError("preflight setup failed")
        install = await run_step(repo.install_cmd, cwd="/home/daytona/repo", timeout=1800)
        tests = await run_step(repo.test_cmd, cwd="/home/daytona/repo", timeout=1800)
        ok = install["exit_code"] == 0 and tests["exit_code"] == 0
    except Exception as exc:  # noqa: BLE001
        error = str(exc)
        ok = False
    finally:
        await mgr.destroy(scan_id)

    return {
        "repo": asdict(repo),
        "ok": ok,
        "error": error,
        "steps": steps,
        "duration_ms": int((time.perf_counter() - started) * 1000),
    }


def choose_first_healthy_medium(preflight_rows: list[dict]) -> dict | None:
    for row in preflight_rows:
        if row.get("ok"):
            return row
    return None


async def _run_combo(repo: RepoTarget, model: ModelTarget, score_target: float) -> dict:
    mgr = SandboxManager()
    scan_id = uuid4()
    owner, name = await parse_repo_url(repo.repo_url)
    info = await get_repo_info(owner, name, token=None)

    started = time.perf_counter()
    steps: list[dict[str, Any]] = []

    async def run_step(
        cmd: str,
        *,
        cwd: str = "/home/daytona",
        timeout: int = 1200,
    ) -> dict[str, Any]:
        step_started = time.perf_counter()
        result = await mgr.exec(scan_id, cmd, cwd=cwd, timeout=timeout)
        row = {
            "cmd": cmd,
            "cwd": cwd,
            "exit_code": int(result.exit_code),
            "duration_ms": int((time.perf_counter() - step_started) * 1000),
            "stdout_tail": _tail(result.stdout, 5000),
        }
        steps.append(row)
        return row

    combo_slug = f"{_slug(repo.label)}-{_slug(model.label)}-{_now_ts()}"
    prompt_path = f"/home/daytona/{combo_slug}.prompt.txt"
    api_key_path = f"/home/daytona/{combo_slug}.openrouter_api_key.txt"
    baseline_path = f"/home/daytona/{combo_slug}.baseline_scan.json"
    post_path = f"/home/daytona/{combo_slug}.post_scan.json"
    openhands_out_path = f"/home/daytona/{combo_slug}.openhands.json"
    final_report: dict[str, Any] = {
        "repo": asdict(repo),
        "model": asdict(model),
        "ok": False,
        "error": None,
        "duration_ms": 0,
        "steps": steps,
    }

    try:
        print(f"[start] {repo.label} :: {model.model}", flush=True)
        await mgr.provision(scan_id, info.clone_url)
        await mgr.upload_file(scan_id, "/home/daytona/quick_scan.py", LOCAL_SCAN_SCRIPT.encode("utf-8"))
        await mgr.upload_file(scan_id, "/home/daytona/openhands_runner.py", OPENHANDS_RUNNER.encode("utf-8"))

        setup_step = await run_step(
            "chmod +x /home/daytona/quick_scan.py /home/daytona/openhands_runner.py && "
            "apt-get update -y && apt-get install -y git nodejs npm && "
            "python3 -m pip install --no-input --upgrade pip && "
            "python3 -m pip install --no-input openhands-sdk bashlex binaryornot libtmux && "
            "python3 -m pip install --no-input --no-deps openhands-tools",
            cwd="/home/daytona",
            timeout=1800,
        )
        if setup_step["exit_code"] != 0:
            raise RuntimeError("sandbox setup failed")

        install_step = await run_step(repo.install_cmd, cwd="/home/daytona/repo", timeout=1800)
        baseline_test_step = await run_step(repo.test_cmd, cwd="/home/daytona/repo", timeout=1800)
        if install_step["exit_code"] != 0:
            raise RuntimeError("baseline install failed")

        scan_before_step = await run_step(
            f"python3 /home/daytona/quick_scan.py /home/daytona/repo > {baseline_path}",
            cwd="/home/daytona",
            timeout=600,
        )
        if scan_before_step["exit_code"] != 0:
            raise RuntimeError("baseline scan failed")
        baseline_scan = json.loads(await mgr.read_file(scan_id, baseline_path))

        prompt_text = _prompt_for_model(model=model.model, repo=repo, baseline_scan=baseline_scan)
        await mgr.upload_file(scan_id, prompt_path, prompt_text.encode("utf-8"))
        await mgr.upload_file(scan_id, api_key_path, settings.openrouter_api_key.encode("utf-8"))
        await run_step(f"chmod 600 {api_key_path}", cwd="/home/daytona", timeout=60)

        run_openhands = await run_step(
            "python3 /home/daytona/openhands_runner.py "
            f"--model 'openrouter/{model.model}' "
            f"--base-url '{settings.openrouter_base_url}' "
            f"--api-key \"$(cat {api_key_path})\" "
            "--workspace /home/daytona/repo "
            f"--prompt-file {prompt_path} "
            f"--out {openhands_out_path}",
            cwd="/home/daytona",
            timeout=2400,
        )

        openhands_result: dict[str, Any] = {}
        if run_openhands["exit_code"] == 0:
            try:
                openhands_result = json.loads(await mgr.read_file(scan_id, openhands_out_path))
            except Exception:
                openhands_result = {"ok": False, "error": "failed to read openhands output"}
        else:
            openhands_result = {"ok": False, "error": "openhands runner command failed"}

        post_test_step = await run_step(repo.test_cmd, cwd="/home/daytona/repo", timeout=1800)
        scan_after_step = await run_step(
            f"python3 /home/daytona/quick_scan.py /home/daytona/repo > {post_path}",
            cwd="/home/daytona",
            timeout=600,
        )
        if scan_after_step["exit_code"] != 0:
            raise RuntimeError("post scan failed")
        post_scan = json.loads(await mgr.read_file(scan_id, post_path))

        changed_files_step = await run_step(
            "git -C /home/daytona/repo diff --name-only | sed '/^$/d' | head -n 200",
            cwd="/home/daytona",
            timeout=120,
        )
        diff_stat_step = await run_step(
            "git -C /home/daytona/repo diff --stat -- . ':(exclude)package-lock.json' | head -n 120",
            cwd="/home/daytona",
            timeout=120,
        )
        branch_step = await run_step(
            "git -C /home/daytona/repo rev-parse --abbrev-ref HEAD",
            cwd="/home/daytona",
            timeout=60,
        )
        doc_step = await run_step(
            "test -f /home/daytona/repo/docs/agent-implementation-note.md && echo yes || echo no",
            cwd="/home/daytona",
            timeout=60,
        )

        before_actionable = int((baseline_scan.get("summary") or {}).get("actionable_count") or 0)
        after_actionable = int((post_scan.get("summary") or {}).get("actionable_count") or 0)
        usage = (openhands_result.get("usage") or {}) if isinstance(openhands_result, dict) else {}
        costs = _calc_costs(int((time.perf_counter() - started) * 1000), usage)
        changed_files = [line.strip() for line in changed_files_step["stdout_tail"].splitlines() if line.strip()]
        final_response = str(openhands_result.get("final_response") or "")
        final_response_json = openhands_result.get("final_response_json")
        active_branch = (branch_step.get("stdout_tail") or "").strip().splitlines()[0] if branch_step.get("stdout_tail") else ""
        implementation_doc_exists = "yes" in (doc_step.get("stdout_tail") or "")
        score = score_run(
            before_actionable=before_actionable,
            after_actionable=after_actionable,
            baseline_tests_exit=int(baseline_test_step["exit_code"]),
            post_tests_exit=int(post_test_step["exit_code"]),
            before_findings=_find_actionable(baseline_scan),
            after_findings=_find_actionable(post_scan),
            final_response=final_response,
            final_response_json=final_response_json if isinstance(final_response_json, dict) else None,
            changed_files=changed_files,
            score_target=score_target,
            active_branch=active_branch,
            implementation_doc_exists=implementation_doc_exists,
        )

        final_report.update(
            {
                "ok": True,
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "baseline": {
                    "tests_exit_code": int(baseline_test_step["exit_code"]),
                    "scan_summary": baseline_scan.get("summary") or {},
                    "actionable_findings": _find_actionable(baseline_scan),
                },
                "post_fix": {
                    "tests_exit_code": int(post_test_step["exit_code"]),
                    "scan_summary": post_scan.get("summary") or {},
                    "actionable_findings": _find_actionable(post_scan),
                },
                "delta": {
                    "actionable_before": before_actionable,
                    "actionable_after": after_actionable,
                    "actionable_reduced": before_actionable - after_actionable,
                    "tests_improved": int(baseline_test_step["exit_code"] != 0 and post_test_step["exit_code"] == 0),
                },
                "scores": score,
                "openhands": openhands_result,
                "active_branch": active_branch,
                "implementation_doc_exists": implementation_doc_exists,
                "changed_files": changed_files,
                "diff_stat_tail": diff_stat_step["stdout_tail"],
                "prompt_path": prompt_path,
                "api_key_path": api_key_path,
                "baseline_scan_path": baseline_path,
                "post_scan_path": post_path,
                "openhands_result_path": openhands_out_path,
                "cost_breakdown": {
                    **costs,
                    "assumptions": {
                        "sandbox_cpu": settings.sandbox_cpu,
                        "sandbox_memory_gb": settings.sandbox_memory_gb,
                        "daytona_vcpu_per_sec_usd": DAYTONA_VCPU_PER_SEC_USD,
                        "daytona_ram_gb_per_sec_usd": DAYTONA_RAM_GB_PER_SEC_USD,
                        "llm_prompt_per_million_usd": LLM_INPUT_PER_MILLION_USD,
                        "llm_completion_per_million_usd": LLM_OUTPUT_PER_MILLION_USD,
                    },
                },
                "sandbox_evidence": {
                    "setup_cmd": setup_step["cmd"],
                    "openhands_cmd": run_openhands["cmd"],
                    "paths": ["/home/daytona/repo", prompt_path, baseline_path, post_path, openhands_out_path],
                },
            }
        )
        print(
            f"[done] {repo.label} :: {model.model} :: total={score['weighted_total']} gate_failed={score['hard_gate_failed']}",
            flush=True,
        )
    except Exception as exc:  # noqa: BLE001
        final_report["ok"] = False
        final_report["error"] = str(exc)
        final_report["duration_ms"] = int((time.perf_counter() - started) * 1000)
        print(f"[error] {repo.label} :: {model.model} :: {exc}", flush=True)
    finally:
        await mgr.destroy(scan_id)
    return final_report


def _run_combo_sync(repo: RepoTarget, model: ModelTarget, score_target: float) -> dict:
    return asyncio.run(_run_combo(repo, model, score_target))


def _run_preflight_sync(repo: RepoTarget) -> dict:
    return asyncio.run(_preflight_repo(repo))


def _rank_key(row: dict) -> tuple:
    scores = row.get("scores") or {}
    total = float(scores.get("weighted_total") or -math.inf)
    gate = bool(scores.get("hard_gate_failed"))
    delta = row.get("delta") or {}
    reduced = int(delta.get("actionable_reduced") or 0)
    duration_ms = int(row.get("duration_ms") or math.inf)
    return (gate, -total, -reduced, duration_ms)


def _model_mean_scores(rows: list[dict]) -> dict[str, float]:
    bucket: dict[str, list[float]] = {}
    for row in rows:
        model = ((row.get("model") or {}).get("model")) or "unknown"
        score = float(((row.get("scores") or {}).get("weighted_total")) or 0.0)
        bucket.setdefault(model, []).append(score)
    return {model: round(sum(vals) / len(vals), 2) for model, vals in bucket.items() if vals}


def _write_markdown(path: Path, payload: dict) -> None:
    lines: list[str] = [
        "# Daytona OpenHands One-Prompt Matrix",
        "",
        f"- Generated at: `{payload.get('generated_at')}`",
        f"- Iterations requested: `{payload.get('config', {}).get('iterations')}`",
        f"- Iterations completed: `{len(payload.get('iterations') or [])}`",
        f"- Score target: `{payload.get('config', {}).get('score_target')}`",
        f"- Worker target: `{payload.get('config', {}).get('target_workers')}`",
        "",
    ]

    for it in payload.get("iterations") or []:
        lines.extend(
            [
                f"## Iteration {it.get('iteration')}",
                f"- Selected medium repo: `{(it.get('selected_medium') or {}).get('repo', {}).get('repo_url', 'n/a')}`",
                f"- Worker cap used: `{it.get('max_workers')}`",
                f"- Hard gate failures: `{it.get('hard_gate_failures')}`",
                f"- Meets target: `{it.get('meets_target')}`",
                "",
                "| Repo | Model | Total | C1 | C2 | C3 | C4 | C5 | Gate Failed |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in it.get("runs") or []:
            scores = row.get("scores") or {}
            c = scores.get("criteria") or {}
            lines.append(
                f"| `{row['repo']['label']}` | `{row['model']['model']}` | "
                f"{float(scores.get('weighted_total') or 0.0):.2f} | "
                f"{float(c.get('c1_one_shot_compliance') or 0.0):.2f} | "
                f"{float(c.get('c2_execution_quality') or 0.0):.2f} | "
                f"{float(c.get('c3_regression_prevention') or 0.0):.2f} | "
                f"{float(c.get('c4_scan_delta_quality') or 0.0):.2f} | "
                f"{float(c.get('c5_delivery_discipline') or 0.0):.2f} | "
                f"`{bool(scores.get('hard_gate_failed'))}` |"
            )
        lines.append("")
    lines.extend(
        [
            "## Raw Artifact",
            f"- JSON: `{payload.get('json_path')}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_canonical_summary(path: Path, payload: dict) -> None:
    latest = (payload.get("iterations") or [])[-1] if payload.get("iterations") else {}
    preflight_rows = latest.get("medium_preflight") or []
    selected_medium = latest.get("selected_medium") or {}
    runs = latest.get("runs") or []
    model_means = latest.get("model_means") or {}

    lines: list[str] = [
        "# One-Shot Matrix Results",
        "",
        "## Latest Run",
        f"- Generated at: `{payload.get('generated_at')}`",
        f"- Iterations completed: `{len(payload.get('iterations') or [])}`",
        f"- Score target: `{payload.get('config', {}).get('score_target')}`",
        f"- Selected medium repo: `{(selected_medium.get('repo') or {}).get('repo_url', 'none')}`",
        "",
        "## Selected Medium Repo and Preflight Evidence",
    ]
    if preflight_rows:
        for row in preflight_rows:
            lines.append(
                f"- `{row['repo']['repo_url']}` -> `{'pass' if row.get('ok') else 'fail'}` "
                f"(duration `{row.get('duration_ms')} ms`)"
            )
    else:
        lines.append("- No preflight evidence recorded.")

    lines.extend(
        [
            "",
            "## Per-Model / Per-Repo Scores",
            "",
            "| Repo | Model | Total | C1 | C2 | C3 | C4 | C5 |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in runs:
        scores = row.get("scores") or {}
        c = scores.get("criteria") or {}
        lines.append(
            f"| `{row['repo']['label']}` | `{row['model']['model']}` | {float(scores.get('weighted_total') or 0.0):.2f} | "
            f"{float(c.get('c1_one_shot_compliance') or 0.0):.2f} | "
            f"{float(c.get('c2_execution_quality') or 0.0):.2f} | "
            f"{float(c.get('c3_regression_prevention') or 0.0):.2f} | "
            f"{float(c.get('c4_scan_delta_quality') or 0.0):.2f} | "
            f"{float(c.get('c5_delivery_discipline') or 0.0):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Before/After Scan Diffs",
        ]
    )
    for row in runs:
        delta = row.get("delta") or {}
        lines.append(
            f"- `{row['repo']['label']}` / `{row['model']['model']}`: "
            f"{delta.get('actionable_before', 0)} -> {delta.get('actionable_after', 0)} "
            f"(delta {delta.get('actionable_reduced', 0)})"
        )

    lines.extend(
        [
            "",
            "## Branch / Doc / User-Loop Compliance",
        ]
    )
    for row in runs:
        checks = ((row.get("scores") or {}).get("checks")) or {}
        lines.append(
            f"- `{row['repo']['label']}` / `{row['model']['model']}`: "
            f"branch={checks.get('branch_ok')} doc={checks.get('implementation_doc_ok')} user_summary={checks.get('user_summary_present')}"
        )

    lines.extend(
        [
            "",
            "## Prompt-Template Changes Between Iterations",
            "- Current run uses strict one-shot contract with required branch/doc/user-loop fields and hard no-follow-up behavior.",
            "",
            "## Final Recommended One-Shot Framework by Provider",
        ]
    )
    for model_name, mean_score in sorted(model_means.items(), key=lambda x: x[1], reverse=True):
        provider = "openai" if model_name.startswith("openai/") else ("anthropic" if model_name.startswith("anthropic/") else "google")
        lines.append(
            f"- `{provider}` -> `{model_name}` (mean score `{mean_score}`), framework: `doc/prompt-guides/ONE_SHOT_IMPLEMENTATION_FRAMEWORK.md`"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one-shot OpenHands remediation matrix in Daytona.")
    parser.add_argument("--target-workers", type=int, default=9)
    parser.add_argument("--pool-cpu", type=int, default=10)
    parser.add_argument("--pool-memory-gb", type=int, default=10)
    parser.add_argument("--pool-storage-gb", type=int, default=30)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--score-target", type=float, default=85.0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    ts = _now_ts()

    settings.sandbox_cpu = MATRIX_SANDBOX_CPU
    settings.sandbox_memory_gb = MATRIX_SANDBOX_MEMORY_GB
    settings.sandbox_disk_gb = MATRIX_SANDBOX_DISK_GB

    easy_repo = RepoTarget(
        label="uuid-easy",
        repo_url="https://github.com/uuidjs/uuid",
        install_cmd="npm install --silent",
        test_cmd="npm test --silent",
    )
    hard_repo = RepoTarget(
        label="express-hard",
        repo_url="https://github.com/expressjs/express",
        install_cmd="npm install --silent",
        test_cmd="npm test --silent",
    )
    medium_candidates = [
        RepoTarget(
            label="requests-medium",
            repo_url="https://github.com/psf/requests",
            install_cmd="python3 -m pip install --no-input -e .",
            test_cmd="python3 -m pytest -q",
        ),
        RepoTarget(
            label="httpx-medium",
            repo_url="https://github.com/encode/httpx",
            install_cmd="python3 -m pip install --no-input -e .",
            test_cmd="python3 -m pytest -q",
        ),
        RepoTarget(
            label="flask-medium",
            repo_url="https://github.com/pallets/flask",
            install_cmd="python3 -m pip install --no-input -e .",
            test_cmd="python3 -m pytest -q",
        ),
    ]
    models = [
        ModelTarget(
            label="openai-gpt5.2-codex",
            model="openai/gpt-5.2-codex",
            guide_path="doc/prompt-guides/openai/codex_prompting_guide.md",
        ),
        ModelTarget(
            label="anthropic-sonnet45",
            model="anthropic/claude-sonnet-4.5",
            guide_path="doc/prompt-guides/anthropic/claude-4-best-practices.md",
        ),
        ModelTarget(
            label="gemini-2.5-pro",
            model="google/gemini-2.5-pro",
            guide_path="doc/prompt-guides/google/prompting-overview.md",
        ),
    ]

    resource_cap = compute_resource_worker_cap(
        pool_cpu=args.pool_cpu,
        pool_memory_gb=args.pool_memory_gb,
        pool_storage_gb=args.pool_storage_gb,
        sandbox_cpu=settings.sandbox_cpu,
        sandbox_memory_gb=settings.sandbox_memory_gb,
        sandbox_disk_gb=settings.sandbox_disk_gb,
    )
    if resource_cap <= 0:
        raise RuntimeError("resource worker cap resolved to zero")

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "target_workers": args.target_workers,
            "pool_cpu": args.pool_cpu,
            "pool_memory_gb": args.pool_memory_gb,
            "pool_storage_gb": args.pool_storage_gb,
            "iterations": args.iterations,
            "score_target": args.score_target,
            "sandbox_cpu": settings.sandbox_cpu,
            "sandbox_memory_gb": settings.sandbox_memory_gb,
            "sandbox_disk_gb": settings.sandbox_disk_gb,
            "resource_worker_cap": resource_cap,
        },
        "matrix_models": [asdict(m) for m in models],
        "iterations": [],
    }

    for iteration in range(1, args.iterations + 1):
        preflight_rows = [_run_preflight_sync(repo) for repo in medium_candidates]
        selected_medium_row = choose_first_healthy_medium(preflight_rows)
        if not selected_medium_row:
            raise RuntimeError("medium repo environment incompatible after preflight remediation")
        medium_repo = RepoTarget(**selected_medium_row["repo"])

        repos = [easy_repo, medium_repo, hard_repo]
        combos = [(repo, model) for repo in repos for model in models]
        max_workers = min(args.target_workers, len(combos), resource_cap)
        rows: list[dict] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(_run_combo_sync, repo, model, args.score_target) for repo, model in combos]
            for fut in concurrent.futures.as_completed(futures):
                rows.append(fut.result())

        model_means = _model_mean_scores(rows)
        hard_gate_failures = sum(1 for row in rows if bool((row.get("scores") or {}).get("hard_gate_failed")))
        meets_target = bool(model_means) and hard_gate_failures == 0 and all(
            score >= args.score_target for score in model_means.values()
        )
        successful = [row for row in rows if row.get("ok")]
        best = sorted(successful, key=_rank_key)[0] if successful else None

        payload["iterations"].append(
            {
                "iteration": iteration,
                "medium_preflight": preflight_rows,
                "selected_medium": selected_medium_row,
                "repos": [asdict(r) for r in repos],
                "max_workers": max_workers,
                "runs": rows,
                "best_run": best,
                "model_means": model_means,
                "hard_gate_failures": hard_gate_failures,
                "meets_target": meets_target,
            }
        )

        if meets_target:
            break

    json_path = RUNS_DIR / f"daytona-openhands-matrix-{ts}.json"
    md_path = RUNS_DIR / f"daytona-openhands-matrix-{ts}.md"
    payload["json_path"] = str(json_path)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(md_path, payload)
    _write_canonical_summary(
        ROOT_DIR / "doc" / "prompt-guides" / "ONE_SHOT_MATRIX_RESULTS.md",
        payload,
    )

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
