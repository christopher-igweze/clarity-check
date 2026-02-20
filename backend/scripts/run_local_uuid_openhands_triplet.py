#!/usr/bin/env python3
"""Run local sequential OpenHands remediation attempts for uuid across 3 models.

This runner uses local machine resources (no Daytona). It mirrors scoring and prompt
generation from the Daytona matrix runner for apples-to-apples comparison.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
RUNS_DIR = ROOT_DIR / "doc" / "runs"
WORK_DIR = RUNS_DIR / "local-uuid-work"


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _log(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {message}", flush=True)


def _slug(value: str) -> str:
    out: list[str] = []
    for ch in str(value).lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in {"-", "_", "/", ".", " "}:
            out.append("-")
    compact = "".join(out).strip("-")
    return "-".join([p for p in compact.split("-") if p])


def _run(cmd: str, cwd: Path, timeout: int = 1200) -> tuple[int, str, str, int]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        duration_ms = int((time.perf_counter() - start) * 1000)
        return int(proc.returncode), proc.stdout or "", proc.stderr or "", duration_ms
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return 124, str(stdout), f"{stderr}\nTIMEOUT after {timeout}s", duration_ms


def _load_matrix_module():
    target = BACKEND_DIR / "scripts" / "run_daytona_openhands_fix_matrix.py"
    spec = importlib.util.spec_from_file_location("matrix_local_helpers", target)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    matrix = _load_matrix_module()
    settings = matrix.settings

    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required in backend/.env")

    openhands_timeout_seconds = 300

    models = [
        matrix.ModelTarget(
            label="openai-gpt5.2-codex",
            model="openai/gpt-5.2-codex",
            guide_path="doc/prompt-guides/openai/codex_prompting_guide.md",
        ),
        matrix.ModelTarget(
            label="anthropic-sonnet45",
            model="anthropic/claude-sonnet-4.5",
            guide_path="doc/prompt-guides/anthropic/claude-4-best-practices.md",
        ),
        matrix.ModelTarget(
            label="gemini-2.5-pro",
            model="google/gemini-2.5-pro",
            guide_path="doc/prompt-guides/google/prompting-overview.md",
        ),
    ]
    repo = matrix.RepoTarget(
        label="uuid-easy-local",
        repo_url="https://github.com/uuidjs/uuid",
        install_cmd="npm install --silent",
        test_cmd="npm test --silent",
    )

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    ts = _now_ts()
    batch_dir = WORK_DIR / f"uuid-triplet-{ts}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for model in models:
        model_slug = _slug(model.label)
        combo_dir = batch_dir / model_slug
        repo_dir = combo_dir / "repo"
        combo_dir.mkdir(parents=True, exist_ok=True)

        _log(f"[{model.model}] cloning uuid")
        rc, so, se, _ = _run(
            "git clone --depth 1 https://github.com/uuidjs/uuid repo",
            cwd=combo_dir,
            timeout=600,
        )
        if rc != 0:
            rows.append(
                {
                    "repo": matrix.asdict(repo),
                    "model": matrix.asdict(model),
                    "ok": False,
                    "error": f"clone failed: {se[-1200:]}",
                    "scores": {"hard_gate_failed": True, "weighted_total": 0.0},
                }
            )
            continue

        quick_scan_path = combo_dir / "quick_scan.py"
        openhands_runner_path = combo_dir / "openhands_runner.py"
        baseline_scan_path = combo_dir / "baseline_scan.json"
        post_scan_path = combo_dir / "post_scan.json"
        prompt_path = combo_dir / "prompt.txt"
        openhands_out_path = combo_dir / "openhands.json"

        quick_scan_path.write_text(matrix.LOCAL_SCAN_SCRIPT, encoding="utf-8")
        openhands_runner_path.write_text(matrix.OPENHANDS_RUNNER, encoding="utf-8")

        _log(f"[{model.model}] install")
        install_rc, _, install_err, _ = _run(repo.install_cmd, cwd=repo_dir, timeout=1800)
        _log(f"[{model.model}] baseline tests")
        base_test_rc, _, _, _ = _run(repo.test_cmd, cwd=repo_dir, timeout=1800)
        _log(f"[{model.model}] baseline scan")
        scan_rc, _, scan_err, _ = _run(
            f"{sys.executable} {quick_scan_path} {repo_dir} > {baseline_scan_path}",
            cwd=combo_dir,
            timeout=600,
        )
        if install_rc != 0 or scan_rc != 0:
            rows.append(
                {
                    "repo": matrix.asdict(repo),
                    "model": matrix.asdict(model),
                    "ok": False,
                    "error": f"baseline failed install_rc={install_rc} scan_rc={scan_rc} install_err={install_err[-600:]} scan_err={scan_err[-600:]}",
                    "scores": {"hard_gate_failed": True, "weighted_total": 0.0},
                }
            )
            continue

        baseline_scan = json.loads(baseline_scan_path.read_text(encoding="utf-8"))
        prompt = matrix._prompt_for_model(
            model=model.model,
            repo=repo,
            baseline_scan=baseline_scan,
            run_id=f"{ts}-{model_slug}",
        )
        prompt_path.write_text(prompt, encoding="utf-8")

        _log(f"[{model.model}] openhands run")
        api_key_path = combo_dir / "openrouter_api_key.txt"
        api_key_path.write_text(settings.openrouter_api_key, encoding="utf-8")

        run_openhands_cmd = (
            f"{sys.executable} {openhands_runner_path} "
            f"--model 'openrouter/{model.model}' "
            f"--base-url '{settings.openrouter_base_url}' "
            f"--api-key \"$(cat {api_key_path})\" "
            f"--workspace '{repo_dir}' "
            f"--prompt-file '{prompt_path}' "
            f"--out '{openhands_out_path}'"
        )
        oh_rc, _, oh_err, _ = _run(
            run_openhands_cmd,
            cwd=combo_dir,
            timeout=openhands_timeout_seconds,
        )
        openhands_result = {"ok": False, "error": f"openhands runner failed: {oh_err[-1200:]}"}
        if oh_rc == 0 and openhands_out_path.exists():
            openhands_result = json.loads(openhands_out_path.read_text(encoding="utf-8"))

        _log(f"[{model.model}] post tests + scan")
        post_test_rc, _, _, _ = _run(repo.test_cmd, cwd=repo_dir, timeout=1800)
        post_scan_rc, _, post_scan_err, _ = _run(
            f"{sys.executable} {quick_scan_path} {repo_dir} > {post_scan_path}",
            cwd=combo_dir,
            timeout=600,
        )
        if post_scan_rc != 0:
            rows.append(
                {
                    "repo": matrix.asdict(repo),
                    "model": matrix.asdict(model),
                    "ok": False,
                    "error": f"post scan failed: {post_scan_err[-1200:]}",
                    "scores": {"hard_gate_failed": True, "weighted_total": 0.0},
                    "openhands": openhands_result,
                }
            )
            continue

        post_scan = json.loads(post_scan_path.read_text(encoding="utf-8"))
        diff_rc, diff_out, _, _ = _run("git diff --name-only", cwd=repo_dir, timeout=120)
        branch_rc, branch_out, _, _ = _run("git rev-parse --abbrev-ref HEAD", cwd=repo_dir, timeout=60)
        doc_exists = (repo_dir / "docs" / "agent-implementation-note.md").exists()

        changed_files = [x.strip() for x in diff_out.splitlines() if x.strip()] if diff_rc == 0 else []
        active_branch = branch_out.strip().splitlines()[0] if branch_rc == 0 and branch_out.strip() else ""
        before_actionable = int((baseline_scan.get("summary") or {}).get("actionable_count") or 0)
        after_actionable = int((post_scan.get("summary") or {}).get("actionable_count") or 0)
        final_response = str(openhands_result.get("final_response") or "")
        final_response_json = (
            openhands_result.get("final_response_json")
            if isinstance(openhands_result.get("final_response_json"), dict)
            else None
        )

        score = matrix.score_run(
            before_actionable=before_actionable,
            after_actionable=after_actionable,
            baseline_tests_exit=base_test_rc,
            post_tests_exit=post_test_rc,
            before_findings=matrix._find_actionable(baseline_scan),
            after_findings=matrix._find_actionable(post_scan),
            final_response=final_response,
            final_response_json=final_response_json,
            changed_files=changed_files,
            score_target=85.0,
            active_branch=active_branch,
            implementation_doc_exists=doc_exists,
        )

        rows.append(
            {
                "repo": matrix.asdict(repo),
                "model": matrix.asdict(model),
                "ok": True,
                "error": None,
                "baseline": {
                    "tests_exit_code": base_test_rc,
                    "scan_summary": baseline_scan.get("summary") or {},
                },
                "post_fix": {
                    "tests_exit_code": post_test_rc,
                    "scan_summary": post_scan.get("summary") or {},
                },
                "delta": {
                    "actionable_before": before_actionable,
                    "actionable_after": after_actionable,
                    "actionable_reduced": before_actionable - after_actionable,
                },
                "scores": score,
                "openhands": openhands_result,
                "active_branch": active_branch,
                "implementation_doc_exists": doc_exists,
                "changed_files": changed_files,
                "paths": {
                    "workspace": str(repo_dir),
                    "prompt": str(prompt_path),
                    "baseline_scan": str(baseline_scan_path),
                    "post_scan": str(post_scan_path),
                    "openhands": str(openhands_out_path),
                },
            }
        )
        _log(
            f"[{model.model}] complete score={score.get('weighted_total')} "
            f"hard_gate_failed={score.get('hard_gate_failed')}"
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "local-sequential",
        "repo": matrix.asdict(repo),
        "models": [matrix.asdict(m) for m in models],
        "runs": rows,
    }
    out_json = RUNS_DIR / f"local-openhands-uuid-triplet-{ts}.json"
    out_md = RUNS_DIR / f"local-openhands-uuid-triplet-{ts}.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Local OpenHands UUID Triplet",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Repo: `{repo.repo_url}`",
        "",
        "| Model | OK | Total | C1 | C2 | C3 | C4 | C5 | Gate Failed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        scores = row.get("scores") or {}
        crit = scores.get("criteria") or {}
        md_lines.append(
            f"| `{row['model']['model']}` | `{row.get('ok')}` | "
            f"{float(scores.get('weighted_total') or 0.0):.2f} | "
            f"{float(crit.get('c1_one_shot_compliance') or 0.0):.2f} | "
            f"{float(crit.get('c2_execution_quality') or 0.0):.2f} | "
            f"{float(crit.get('c3_regression_prevention') or 0.0):.2f} | "
            f"{float(crit.get('c4_scan_delta_quality') or 0.0):.2f} | "
            f"{float(crit.get('c5_delivery_discipline') or 0.0):.2f} | "
            f"`{bool(scores.get('hard_gate_failed'))}` |"
        )
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    _log(f"artifacts json={out_json}")
    _log(f"artifacts md={out_md}")

    # Keep workspaces for forensic review by default.
    _log(f"workspace root={batch_dir}")


if __name__ == "__main__":
    main()
