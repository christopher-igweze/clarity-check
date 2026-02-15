"""Agent_Builder — The SRE (DeepSeek V3.2).

Performs dynamic analysis: runs the application inside the sandbox,
executes tests, attempts builds, hits endpoints, and captures screenshots.
Produces objective, verifiable proof of what works and what doesn't.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any
from uuid import UUID

from models.agent_log import AgentName, LogLevel, SSEEventType
from models.findings import Finding, ProbeResult, Category, Severity, FindingSource
from services.context_store import ContextStore

from agents.base_agent import BaseVibe2ProdAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Agent_Builder, a Senior Site Reliability Engineer.  You have full
terminal access to a cloned repository at $WORKSPACE_DIR.

Your mission is to DYNAMICALLY PROBE the application — actually run it and
see what happens.  Do not just read code; execute it.

Steps (run each, capture exit code + output):
1. **Dependency Install**: `npm install` (or `pip install -r requirements.txt`)
   — Does it install cleanly?  Note warnings/errors.
2. **Build Test**: `npm run build` (or equivalent)
   — Does it compile?  Capture any build errors.
3. **Unit Tests**: `npm test` (or `pytest`)
   — How many pass/fail?  Capture the summary.
4. **Dependency Audit**: `npm audit --json` (or `pip-audit --format json`)
   — How many known CVEs?
5. **Startup Test**: ONLY run a dev server using a hard timeout so the command exits.
   - Prefer: `timeout 10s npm run dev -- --host 0.0.0.0 --port 18080`
   - Or: `timeout 10s npm start`
   If `timeout` exits with code 124, that's OK *as long as* you observed the server started.
6. **Lint Check**: `npx eslint . --format json` (if configured)
   — How many warnings/errors?

For each step, report:
{
  "step": "install" | "build" | "test" | "audit" | "startup" | "lint",
  "passed": true | false,
  "exit_code": 0,
  "stdout": "first 500 chars of stdout",
  "stderr": "first 500 chars of stderr",
  "duration_ms": 1234
}

Also identify any DYNAMIC findings (issues only discoverable by running
the code) as:
{
  "title": "...",
  "description": "...",
  "category": "reliability" | "security" | "scalability",
  "severity": "critical" | "high" | "medium" | "low",
  "source": "dynamic",
  "file_path": "..." (if applicable),
  "line_number": null
}

Output a JSON object with two keys:
{
  "probe_results": [...],
  "findings": [...]
}

Be factual.  Only report what you actually observed — never fabricate results.
"""


class BuilderAgent(BaseVibe2ProdAgent):
    agent_name = AgentName.builder
    model_config_key = "model_builder"
    system_prompt = SYSTEM_PROMPT

    async def run(self) -> tuple[list[ProbeResult], list[Finding]]:
        """Run the dynamic probe and return results + findings."""
        self._log("Starting dynamic probe — running the application...")

        probe_results, findings = await self._run_local_probes()

        # Store in context
        self.context.set(
            "probe:results",
            [p.model_dump(mode="json") for p in probe_results],
        )
        self.context.set(
            "findings:builder",
            [f.model_dump(mode="json") for f in findings],
        )

        # Emit probe results
        for p in probe_results:
            status = "PASS" if p.passed else "FAIL"
            level = LogLevel.success if p.passed else LogLevel.error
            self._log(
                f"[{status}] {p.step} (exit {p.exit_code}, {p.duration_ms}ms)",
                level=level,
                event_type=SSEEventType.probe_result,
                data=p.model_dump(mode="json"),
            )

        # Emit dynamic findings
        for f in findings:
            self._log(
                f"[DYNAMIC] [{f.severity.value.upper()}] {f.title}",
                level=LogLevel.warn,
                event_type=SSEEventType.finding,
                data=f.model_dump(mode="json"),
            )

        self._log(
            f"Dynamic probe complete: {sum(1 for p in probe_results if p.passed)}/{len(probe_results)} steps passed, "
            f"{len(findings)} dynamic issues found",
            level=LogLevel.success,
            event_type=SSEEventType.agent_complete,
        )

        return probe_results, findings

    async def _run_local_probes(self) -> tuple[list[ProbeResult], list[Finding]]:
        """Execute deterministic probe steps locally (no LLM/tool-calling)."""
        workspace = Path(self.workspace_dir)
        if not workspace.exists():
            return [], [
                Finding(
                    title="Workspace directory missing",
                    description=f"Expected workspace at {self.workspace_dir} but it does not exist.",
                    category=Category.reliability,
                    severity=Severity.critical,
                    source=FindingSource.dynamic,
                    agent="Agent_Builder",
                )
            ]

        # Currently only supports Node projects.
        if not (workspace / "package.json").exists():
            self._log(
                "No package.json found; skipping dynamic probes.",
                level=LogLevel.warn,
            )
            return [], []

        async def run_cmd(
            step: str, cmd: list[str], timeout_s: int
        ) -> ProbeResult:
            start = time.monotonic()
            try:
                proc = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    cwd=str(workspace),
                    capture_output=True,
                    text=True,
                    timeout=timeout_s,
                )
                stdout = (proc.stdout or "")[:2000]
                stderr = (proc.stderr or "")[:2000]
                return ProbeResult(
                    step=step,
                    passed=(proc.returncode == 0),
                    exit_code=proc.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            except subprocess.TimeoutExpired as exc:
                stdout = (exc.stdout or "")[:2000] if isinstance(exc.stdout, str) else ""
                stderr = (exc.stderr or "")[:2000] if isinstance(exc.stderr, str) else ""
                return ProbeResult(
                    step=step,
                    passed=False,
                    exit_code=124,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            except Exception as exc:
                return ProbeResult(
                    step=step,
                    passed=False,
                    exit_code=1,
                    stdout="",
                    stderr=str(exc)[:2000],
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

        probes: list[ProbeResult] = []
        findings: list[Finding] = []

        # 1) Install
        install = await run_cmd("install", ["npm", "install"], timeout_s=600)
        probes.append(install)
        if not install.passed:
            findings.append(
                Finding(
                    title="Dependency install failed",
                    description=(
                        "Running `npm install` failed. This blocks build/test/lint.\n\n"
                        f"stdout (truncated):\n{install.stdout}\n\n"
                        f"stderr (truncated):\n{install.stderr}"
                    ),
                    category=Category.reliability,
                    severity=Severity.critical,
                    source=FindingSource.dynamic,
                    agent="Agent_Builder",
                )
            )
            return probes, findings

        # 2) Build
        build = await run_cmd("build", ["npm", "run", "build"], timeout_s=600)
        probes.append(build)
        if not build.passed:
            findings.append(
                Finding(
                    title="Build failed",
                    description=(
                        "Running `npm run build` failed.\n\n"
                        f"stdout (truncated):\n{build.stdout}\n\n"
                        f"stderr (truncated):\n{build.stderr}"
                    ),
                    category=Category.reliability,
                    severity=Severity.high,
                    source=FindingSource.dynamic,
                    agent="Agent_Builder",
                )
            )

        # 3) Tests
        test = await run_cmd("test", ["npm", "test"], timeout_s=600)
        probes.append(test)
        if not test.passed:
            findings.append(
                Finding(
                    title="Tests failing",
                    description=(
                        "Running `npm test` failed.\n\n"
                        f"stdout (truncated):\n{test.stdout}\n\n"
                        f"stderr (truncated):\n{test.stderr}"
                    ),
                    category=Category.reliability,
                    severity=Severity.high,
                    source=FindingSource.dynamic,
                    agent="Agent_Builder",
                )
            )

        # 4) Audit (npm exits non-zero when vulnerabilities exist)
        audit = await run_cmd("audit", ["npm", "audit", "--json"], timeout_s=180)
        probes.append(audit)
        try:
            audit_data = json.loads(audit.stdout or "{}")
            vulns = (audit_data.get("metadata") or {}).get("vulnerabilities") or {}
            critical = int(vulns.get("critical") or 0)
            high = int(vulns.get("high") or 0)
            moderate = int(vulns.get("moderate") or 0)
            low = int(vulns.get("low") or 0)
            total = critical + high + moderate + low
            if total > 0:
                sev = (
                    Severity.critical
                    if critical > 0
                    else Severity.high
                    if high > 0
                    else Severity.medium
                )
                findings.append(
                    Finding(
                        title="Dependency vulnerabilities detected (npm audit)",
                        description=(
                            f"`npm audit` reports vulnerabilities: critical={critical}, high={high}, "
                            f"moderate={moderate}, low={low}.\n\n"
                            "Recommended next steps:\n"
                            "- Run `npm audit fix` (and review the diff)\n"
                            "- If fixes require breaking changes, plan upgrades intentionally\n"
                        ),
                        category=Category.security,
                        severity=sev,
                        source=FindingSource.dynamic,
                        agent="Agent_Builder",
                    )
                )
        except Exception:
            # If audit output isn't JSON, leave probe result as-is.
            pass

        # 5) Lint (repo script)
        lint = await run_cmd("lint", ["npm", "run", "lint"], timeout_s=600)
        probes.append(lint)
        if not lint.passed:
            findings.append(
                Finding(
                    title="Lint errors",
                    description=(
                        "Running `npm run lint` failed.\n\n"
                        f"stdout (truncated):\n{lint.stdout}\n\n"
                        f"stderr (truncated):\n{lint.stderr}"
                    ),
                    category=Category.reliability,
                    severity=Severity.medium,
                    source=FindingSource.dynamic,
                    agent="Agent_Builder",
                )
            )

        return probes, findings

    def _parse_output(
        self, raw: str
    ) -> tuple[list[ProbeResult], list[Finding]]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    data = json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    logger.warning("Builder output is not valid JSON")
                    return [], []
            else:
                return [], []

        probes = []
        for item in data.get("probe_results", []):
            try:
                probes.append(
                    ProbeResult(
                        step=item["step"],
                        passed=item.get("passed", False),
                        exit_code=item.get("exit_code", 1),
                        stdout=item.get("stdout", "")[:2000],
                        stderr=item.get("stderr", "")[:2000],
                        duration_ms=item.get("duration_ms", 0),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping malformed probe result: %s", exc)

        findings = []
        for item in data.get("findings", []):
            try:
                findings.append(
                    Finding(
                        title=item.get("title", "Untitled"),
                        description=item.get("description", ""),
                        category=Category(item.get("category", "reliability")),
                        severity=Severity(item.get("severity", "medium")),
                        source=FindingSource.dynamic,
                        file_path=item.get("file_path"),
                        line_number=item.get("line_number"),
                        agent="Agent_Builder",
                    )
                )
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed finding: %s", exc)

        return probes, findings
