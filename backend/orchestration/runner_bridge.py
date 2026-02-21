"""Runner bridge that normalizes task execution outcomes for runtime ticks."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import timedelta
from importlib import import_module
import json
import re
import shlex
from uuid import UUID, uuid4

from config import settings
from models.builds import BuildRun
from models.runtime import RuntimeRunLog, utc_now
from orchestration.execution_policy import NodePolicyResult, evaluate_node_execution_policy

_MAX_LOGS_PER_BUILD = 3000
_DAYTONA_SHELL_RUNNER_KINDS = {"daytona_shell"}
_OPENHANDS_DAYTONA_RUNNER_KINDS = {"openhands_daytona", "daytona-openhands", "daytona_openhands"}
_OPENHANDS_NODE_RUNNER_PATH = "/home/daytona/openhands_node_runner.py"
_OPENHANDS_API_KEY_PATH = "/home/daytona/.openrouter_api_key.txt"

_STATUS_MAP = {
    "ok": "completed",
    "pass": "completed",
    "success": "completed",
    "completed": "completed",
    "done": "completed",
    "fail": "failed",
    "failed": "failed",
    "error": "failed",
    "errored": "failed",
    "skip": "skipped",
    "skipped": "skipped",
}

_OPENHANDS_NODE_RUNNER = """#!/usr/bin/env python3
import argparse
import json
import traceback

def _emit(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--objective-file", required=True)
    parser.add_argument("--api-key-file", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--max-output", type=int, default=4096)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    try:
        with open(args.objective_file, "r", encoding="utf-8") as f:
            objective = f.read()
        with open(args.api_key_file, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
    except Exception as exc:
        _emit(args.out, {
            "status": "failed",
            "summary": "failed to read objective/api key",
            "error": str(exc),
        })
        return 0

    try:
        from pydantic import SecretStr
        from openhands.sdk import LLM, Agent, Conversation, Tool
        from openhands.tools.terminal import TerminalTool
        from openhands.tools.file_editor import FileEditorTool
        from openhands.sdk.conversation.response_utils import get_agent_final_response
    except Exception as exc:
        _emit(args.out, {
            "status": "failed",
            "summary": "openhands runtime is unavailable in workspace",
            "error": str(exc),
        })
        return 0

    prompt = (
        "You are executing a single DAG node in a controlled orchestration runtime.\\n"
        f"Node: {args.node_id}\\n\\n"
        f"{objective}\\n\\n"
        "Execution policy:\\n"
        "- Use only terminal/file_editor/think/finish style actions.\\n"
        "- Do not use destructive git operations.\\n"
        "- Finish with concise JSON in plain text (no markdown fences).\\n"
        "- JSON keys: status, summary, notes.\\n"
    )
    try:
        llm = LLM(
            model=f"openrouter/{args.model}",
            api_key=SecretStr(api_key),
            base_url=args.base_url,
            max_output_tokens=max(256, int(args.max_output)),
        )
        agent = Agent(
            llm=llm,
            tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)],
        )
        conv = Conversation(agent=agent, workspace=args.workspace)
        conv.send_message(prompt)
        conv.run()

        final_response = ""
        try:
            events = getattr(conv.state, "events", None)
            if events is not None:
                final_response = (get_agent_final_response(events) or "").strip()
        except Exception:
            final_response = ""

        payload = {
            "status": "completed",
            "summary": final_response or f"OpenHands completed node {args.node_id}",
            "raw": final_response,
        }
        try:
            parsed = json.loads(final_response) if final_response else {}
            if isinstance(parsed, dict):
                payload.update(parsed)
        except Exception:
            pass

        status = str(payload.get("status", "completed")).strip().lower()
        if status not in {"completed", "failed", "skipped"}:
            payload["status"] = "completed"
        _emit(args.out, payload)
        return 0
    except Exception as exc:
        _emit(args.out, {
            "status": "failed",
            "summary": f"OpenHands execution failed for node {args.node_id}",
            "error": str(exc),
            "traceback": traceback.format_exc(limit=5),
        })
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""


def normalize_runner_status(raw_status: object) -> str:
    if not isinstance(raw_status, str):
        return "completed"
    return _STATUS_MAP.get(raw_status.strip().lower(), "completed")


class RunnerBridge:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._logs: dict[UUID, list[RuntimeRunLog]] = defaultdict(list)
        self._sandbox_manager = None
        self._active_daytona_workspaces: dict[UUID, str] = {}
        self._workspace_image_profiles: dict[UUID, str] = {}
        self._openhands_runtime_ready: dict[UUID, bool] = {}

    async def execute(
        self,
        *,
        build: BuildRun,
        runtime_id: UUID,
        node_id: str,
    ) -> RuntimeRunLog:
        runner_kind = str(build.metadata.get("runner_kind") or "").strip().lower()
        node_overrides = self._resolve_node_override(build, node_id)
        resolved_runner = str(
            runner_kind
            or node_overrides.get("runner")
            or build.metadata.get("runner_kind")
            or "openhands"
        ).strip().lower()
        planned_command = self._planned_command_for_policy(
            build=build,
            node_id=node_id,
            runner_kind=resolved_runner,
            node_overrides=node_overrides,
        )
        policy_result = evaluate_node_execution_policy(
            build=build,
            node_id=node_id,
            runner_kind=resolved_runner,
            command=planned_command,
        )
        if not policy_result.allowed:
            record = self._policy_blocked_record(
                build=build,
                runtime_id=runtime_id,
                node_id=node_id,
                runner=resolved_runner or "policy_guard",
                policy_result=policy_result,
                command=planned_command,
            )
            async with self._lock:
                self._append_record(build.build_id, record)
            return record

        if runner_kind in _OPENHANDS_DAYTONA_RUNNER_KINDS:
            record = await self._execute_openhands_daytona(
                build=build,
                runtime_id=runtime_id,
                node_id=node_id,
            )
            async with self._lock:
                self._append_record(build.build_id, record)
            return record

        if runner_kind in _DAYTONA_SHELL_RUNNER_KINDS:
            record = await self._execute_daytona(
                build=build,
                runtime_id=runtime_id,
                node_id=node_id,
            )
            async with self._lock:
                self._append_record(build.build_id, record)
            return record

        async with self._lock:
            self._advance_override_sequences(node_overrides)
            runner = str(node_overrides.get("runner") or build.metadata.get("runner_kind") or "openhands")
            workspace_id = str(
                node_overrides.get("workspace_id")
                or build.metadata.get("workspace_id")
                or f"daytona-{build.build_id}"
            )
            status = normalize_runner_status(node_overrides.get("status"))
            duration_ms = self._normalize_duration(node_overrides.get("duration_ms"))
            message = str(node_overrides.get("message") or f"{runner} executed {node_id}")
            error = str(node_overrides.get("error")) if status == "failed" and node_overrides.get("error") else None
            exit_code = int(node_overrides.get("exit_code", 1 if status == "failed" else 0))

            started_at = utc_now()
            finished_at = started_at + timedelta(milliseconds=duration_ms)
            record = RuntimeRunLog(
                log_id=uuid4(),
                build_id=build.build_id,
                runtime_id=runtime_id,
                node_id=node_id,
                runner=runner,
                workspace_id=workspace_id,
                status=status,  # type: ignore[arg-type]
                message=message,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                error=error,
                metadata={
                    "exit_code": exit_code,
                    "agent": self._resolve_agent_name(build, node_id),
                },
            )
            self._append_record(build.build_id, record)
            return record

    async def _execute_daytona(
        self,
        *,
        build: BuildRun,
        runtime_id: UUID,
        node_id: str,
    ) -> RuntimeRunLog:
        node_overrides = self._resolve_node_override(build, node_id)
        command = str(
            node_overrides.get("command")
            or self._default_daytona_command(build=build, node_id=node_id)
        )
        timeout_seconds = max(30, int(node_overrides.get("timeout_seconds", 180)))
        started_at = utc_now()
        workspace_id = str(
            node_overrides.get("workspace_id") or f"daytona-{build.build_id}"
        )
        status = "completed"
        error: str | None = None
        message = str(node_overrides.get("message") or f"daytona_shell executed {node_id}")
        exit_code = 0
        stdout = ""
        stderr = ""

        try:
            workspace_id, exit_code, stdout, stderr = await self._run_daytona_command(
                build=build,
                command=command,
                timeout_seconds=timeout_seconds,
            )
            status = "completed" if int(exit_code) == 0 else "failed"
            if status == "failed":
                error = (
                    str(node_overrides.get("error") or "").strip()
                    or stderr.strip()
                    or stdout.strip()
                    or f"daytona_command_failed_exit_{exit_code}"
                )
        except Exception as exc:
            status = "failed"
            error = str(exc)
            message = f"daytona_shell failed for {node_id}"

        finished_at = utc_now()
        duration_ms = max(
            1,
            int((finished_at - started_at).total_seconds() * 1000),
        )
        return RuntimeRunLog(
            log_id=uuid4(),
            build_id=build.build_id,
            runtime_id=runtime_id,
            node_id=node_id,
            runner="daytona_shell",
            workspace_id=workspace_id,
            status=status,  # type: ignore[arg-type]
            message=message,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            error=error,
            metadata={
                "exit_code": int(exit_code),
                "agent": self._resolve_agent_name(build, node_id),
                "command": command,
                "timeout_seconds": timeout_seconds,
                "execution_mode": "daytona_shell",
                "stdout_preview": stdout[:1200],
                "stderr_preview": stderr[:1200],
            },
        )

    async def _execute_openhands_daytona(
        self,
        *,
        build: BuildRun,
        runtime_id: UUID,
        node_id: str,
    ) -> RuntimeRunLog:
        node_overrides = self._resolve_node_override(build, node_id)
        timeout_seconds = max(45, int(node_overrides.get("timeout_seconds", 420)))
        started_at = utc_now()
        exit_code = 0
        stdout = ""
        stderr = ""
        error: str | None = None
        status = "completed"
        workspace_id = str(node_overrides.get("workspace_id") or f"daytona-{build.build_id}")
        safe_node_id = _safe_node_id(node_id)
        objective_path = f"/home/daytona/.openhands_objective_{safe_node_id}.txt"
        output_path = f"/home/daytona/.openhands_result_{safe_node_id}.json"
        objective = str(
            node_overrides.get("prompt")
            or self._default_openhands_objective(build=build, node_id=node_id)
        )
        result_payload: dict[str, object] = {}
        message = f"OpenHands executed {node_id}"
        model = str(node_overrides.get("model") or self._model_for_agent(build, node_id))

        try:
            await self._ensure_openhands_daytona_runtime(build)
            manager = self._get_sandbox_manager()
            await manager.upload_file(build.build_id, objective_path, objective.encode("utf-8"))
            command = " ".join(
                [
                    "python3",
                    shlex.quote(_OPENHANDS_NODE_RUNNER_PATH),
                    "--workspace",
                    shlex.quote("/home/daytona/repo"),
                    "--node-id",
                    shlex.quote(node_id),
                    "--model",
                    shlex.quote(model),
                    "--objective-file",
                    shlex.quote(objective_path),
                    "--api-key-file",
                    shlex.quote(_OPENHANDS_API_KEY_PATH),
                    "--base-url",
                    shlex.quote(settings.openrouter_base_url),
                    "--max-output",
                    str(max(256, int(settings.llm_max_output_tokens))),
                    "--out",
                    shlex.quote(output_path),
                ]
            )
            workspace_id, exit_code, stdout, stderr = await self._run_daytona_command(
                build=build,
                command=command,
                timeout_seconds=timeout_seconds,
                image_profile="openhands_runtime",
            )
            try:
                raw_output = await manager.read_file(build.build_id, output_path)
                parsed = json.loads(raw_output)
                if isinstance(parsed, dict):
                    result_payload = parsed
            except Exception:
                result_payload = {}
        except Exception as exc:
            status = "failed"
            error = str(exc)

        if status != "failed":
            payload_status = normalize_runner_status(result_payload.get("status"))
            status = payload_status
            message = str(
                result_payload.get("summary")
                or node_overrides.get("message")
                or message
            )
            if status == "failed":
                error = (
                    str(result_payload.get("error") or "").strip()
                    or stderr.strip()
                    or stdout.strip()
                    or f"openhands_daytona_failed_exit_{exit_code}"
                )

        finished_at = utc_now()
        duration_ms = max(1, int((finished_at - started_at).total_seconds() * 1000))
        return RuntimeRunLog(
            log_id=uuid4(),
            build_id=build.build_id,
            runtime_id=runtime_id,
            node_id=node_id,
            runner="openhands_daytona",
            workspace_id=workspace_id,
            status=status,  # type: ignore[arg-type]
            message=message,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            error=error,
            metadata={
                "exit_code": int(exit_code),
                "agent": self._resolve_agent_name(build, node_id),
                "execution_mode": "openhands_daytona",
                "model": model,
                "objective_path": objective_path,
                "output_path": output_path,
                "timeout_seconds": timeout_seconds,
                "stdout_preview": stdout[:1200],
                "stderr_preview": stderr[:1200],
                "payload": result_payload,
            },
        )

    async def _run_daytona_command(
        self,
        *,
        build: BuildRun,
        command: str,
        timeout_seconds: int,
        image_profile: str | None = None,
    ) -> tuple[str, int, str, str]:
        workspace_id = await self._ensure_daytona_workspace(
            build,
            image_profile=image_profile,
        )
        manager = self._get_sandbox_manager()
        result = await manager.exec(
            build.build_id,
            command=command,
            timeout=timeout_seconds,
        )
        return (
            workspace_id,
            int(getattr(result, "exit_code", 1)),
            str(getattr(result, "stdout", "") or ""),
            str(getattr(result, "stderr", "") or ""),
        )

    def _get_sandbox_manager(self):
        if self._sandbox_manager is not None:
            return self._sandbox_manager
        module = import_module("sandbox.manager")
        self._sandbox_manager = module.SandboxManager()
        return self._sandbox_manager

    async def _ensure_daytona_workspace(
        self,
        build: BuildRun,
        *,
        image_profile: str | None = None,
    ) -> str:
        requested_profile = str(image_profile or "default").strip().lower() or "default"
        async with self._lock:
            existing = self._active_daytona_workspaces.get(build.build_id)
            existing_profile = self._workspace_image_profiles.get(build.build_id, "default")
        if existing is not None:
            if existing_profile != requested_profile:
                raise RuntimeError(
                    "daytona_workspace_profile_conflict:"
                    f"requested={requested_profile}:active={existing_profile}"
                )
            return existing

        manager = self._get_sandbox_manager()
        session = await manager.provision(
            build.build_id,
            build.repo_url,
            image_profile=image_profile,
        )
        workspace_id = str(
            getattr(session.sandbox, "id", None)
            or getattr(session, "repo_path", None)
            or f"daytona-{build.build_id}"
        )
        async with self._lock:
            self._active_daytona_workspaces[build.build_id] = workspace_id
            self._workspace_image_profiles[build.build_id] = requested_profile
        return workspace_id

    async def _ensure_openhands_daytona_runtime(self, build: BuildRun) -> None:
        async with self._lock:
            if self._openhands_runtime_ready.get(build.build_id):
                return

        manager = self._get_sandbox_manager()
        runtime_image = str(settings.daytona_openhands_runtime_image or "").strip()
        if not runtime_image:
            raise RuntimeError(
                "OpenHands runtime image is not configured. "
                "Set DAYTONA_OPENHANDS_RUNTIME_IMAGE to a hardened prebuilt image."
            )

        await self._ensure_daytona_workspace(build, image_profile="openhands_runtime")
        await manager.upload_file(
            build.build_id,
            _OPENHANDS_NODE_RUNNER_PATH,
            _OPENHANDS_NODE_RUNNER.encode("utf-8"),
        )
        await manager.upload_file(
            build.build_id,
            _OPENHANDS_API_KEY_PATH,
            settings.openrouter_api_key.encode("utf-8"),
        )
        await manager.exec(
            build.build_id,
            command=f"chmod 700 {shlex.quote(_OPENHANDS_NODE_RUNNER_PATH)} && chmod 600 {shlex.quote(_OPENHANDS_API_KEY_PATH)}",
            cwd="/home/daytona",
            timeout=90,
        )

        verify_cmd = (
            "python3 - <<'PY'\n"
            "import importlib.util\n"
            "mods=['openhands.sdk','openhands.tools.terminal','openhands.tools.file_editor','pydantic']\n"
            "missing=[m for m in mods if importlib.util.find_spec(m) is None]\n"
            "if missing:\n"
            "  raise SystemExit('missing_runtime_modules:' + ','.join(missing))\n"
            "print('openhands_runtime_ready')\n"
            "PY"
        )
        verify = await manager.exec(
            build.build_id,
            command=verify_cmd,
            cwd="/home/daytona",
            timeout=90,
        )
        if int(getattr(verify, "exit_code", 1)) != 0:
            stderr = str(getattr(verify, "stderr", "") or "").strip()
            stdout = str(getattr(verify, "stdout", "") or "").strip()
            details = stderr or stdout or "runtime verification failed"
            raise RuntimeError(
                "OpenHands runtime image is missing required modules: "
                f"{details}. Rebuild image '{runtime_image}' with openhands-sdk and tools."
            )

        async with self._lock:
            self._openhands_runtime_ready[build.build_id] = True

    async def finalize_build(self, build_id: UUID) -> None:
        async with self._lock:
            active = build_id in self._active_daytona_workspaces
            self._active_daytona_workspaces.pop(build_id, None)
            self._workspace_image_profiles.pop(build_id, None)
            self._openhands_runtime_ready.pop(build_id, None)
        if not active:
            return
        try:
            manager = self._get_sandbox_manager()
            await manager.destroy(build_id)
        except Exception:
            # Runtime completion should not fail on cleanup errors.
            return

    async def list_logs(
        self,
        *,
        build_id: UUID,
        node_id: str | None = None,
        status: str | None = None,
        limit: int = 200,
    ) -> list[RuntimeRunLog]:
        async with self._lock:
            rows = list(self._logs.get(build_id, []))
        if node_id:
            rows = [row for row in rows if row.node_id == node_id]
        if status:
            normalized = normalize_runner_status(status)
            rows = [row for row in rows if row.status == normalized]
        rows.sort(key=lambda row: row.started_at, reverse=True)
        return rows[: max(1, min(limit, 1000))]

    async def reset(self) -> None:
        async with self._lock:
            self._logs.clear()
            active_build_ids = list(self._active_daytona_workspaces.keys())
            self._active_daytona_workspaces.clear()
            self._workspace_image_profiles.clear()
            self._openhands_runtime_ready.clear()
        for build_id in active_build_ids:
            try:
                manager = self._get_sandbox_manager()
                await manager.destroy(build_id)
            except Exception:
                continue

    @staticmethod
    def _resolve_node_override(build: BuildRun, node_id: str) -> dict:
        raw = build.metadata.get("runner_results")
        if not isinstance(raw, dict):
            return {}
        node = raw.get(node_id)
        return node if isinstance(node, dict) else {}

    @staticmethod
    def _resolve_agent_name(build: BuildRun, node_id: str) -> str:
        node = next((item for item in build.dag if item.node_id == node_id), None)
        return node.agent if node is not None else "unknown"

    @staticmethod
    def _model_for_agent(build: BuildRun, node_id: str) -> str:
        node = next((item for item in build.dag if item.node_id == node_id), None)
        agent = (node.agent if node is not None else "").strip().lower()
        if agent == "scanner":
            return settings.model_scanner
        if agent == "builder":
            return settings.model_builder
        if agent == "security":
            return settings.model_security
        if agent in {"planner", "verifier"}:
            return settings.model_planner
        if agent == "educator":
            return settings.model_educator
        return settings.model_planner

    @staticmethod
    def _default_openhands_objective(*, build: BuildRun, node_id: str) -> str:
        node = next((item for item in build.dag if item.node_id == node_id), None)
        title = node.title if node is not None else node_id
        agent = node.agent if node is not None else "generalist"
        return (
            f"Repository: {build.repo_url}\n"
            f"Build objective: {build.objective}\n"
            f"DAG node: {node_id}\n"
            f"Node title: {title}\n"
            f"Assigned role: {agent}\n\n"
            "Task requirements:\n"
            "1) Inspect relevant files and current project state.\n"
            "2) Execute only minimal changes/commands required for this node.\n"
            "3) If tests/build exist, run targeted verification commands.\n"
            "4) Summarize outcome and unresolved risks.\n"
            "5) Do not perform destructive git operations.\n"
        )

    @staticmethod
    def _default_daytona_command(*, build: BuildRun, node_id: str) -> str:
        node = next((item for item in build.dag if item.node_id == node_id), None)
        agent = (node.agent if node is not None else "").strip().lower()

        if agent == "scanner":
            return "pwd && ls -la && echo '[scanner] repo inventory complete'"
        if agent == "builder":
            return (
                "if [ -f package.json ]; then npm test --silent; "
                "elif [ -f pyproject.toml ] || [ -f requirements.txt ]; then pytest -q; "
                "else echo '[builder] no test command inferred'; fi"
            )
        if agent == "security":
            return (
                "if command -v rg >/dev/null 2>&1; then "
                "rg -n \"(password|secret|token|api[_-]?key)\" . || true; "
                "else grep -Rni \"password\\|secret\\|token\\|api[_-]*key\" . || true; fi"
            )
        if agent == "planner":
            return "echo '[planner] summarize findings and produce remediation plan'"
        return "echo '[executor] completed generic node task'"

    @staticmethod
    def _advance_override_sequences(node_overrides: dict) -> None:
        status_sequence = node_overrides.get("status_sequence")
        if isinstance(status_sequence, list) and status_sequence:
            node_overrides["status"] = status_sequence.pop(0)

        error_sequence = node_overrides.get("error_sequence")
        if isinstance(error_sequence, list) and error_sequence:
            node_overrides["error"] = error_sequence.pop(0)

    @staticmethod
    def _normalize_duration(raw: object) -> int:
        if isinstance(raw, int):
            return max(0, raw)
        if isinstance(raw, float):
            return max(0, int(raw))
        return 250

    @staticmethod
    def _planned_command_for_policy(
        *,
        build: BuildRun,
        node_id: str,
        runner_kind: str,
        node_overrides: dict,
    ) -> str | None:
        override_command = node_overrides.get("command")
        if isinstance(override_command, str) and override_command.strip():
            return override_command

        normalized_runner = runner_kind.strip().lower()
        if normalized_runner in _DAYTONA_SHELL_RUNNER_KINDS:
            return RunnerBridge._default_daytona_command(build=build, node_id=node_id)
        return None

    @staticmethod
    def _policy_blocked_record(
        *,
        build: BuildRun,
        runtime_id: UUID,
        node_id: str,
        runner: str,
        policy_result: NodePolicyResult,
        command: str | None,
    ) -> RuntimeRunLog:
        now = utc_now()
        violation = {
            "code": policy_result.code or "policy_blocked",
            "message": policy_result.message or "Execution blocked by policy.",
            "source": "execution_policy",
            "blocking": True,
            "details": policy_result.details or {},
        }
        return RuntimeRunLog(
            log_id=uuid4(),
            build_id=build.build_id,
            runtime_id=runtime_id,
            node_id=node_id,
            runner=runner,
            workspace_id=str(build.metadata.get("workspace_id") or f"daytona-{build.build_id}"),
            status="failed",
            message=violation["message"],
            started_at=now,
            finished_at=now,
            duration_ms=1,
            error=violation["message"],
            metadata={
                "exit_code": 1,
                "agent": RunnerBridge._resolve_agent_name(build, node_id),
                "execution_mode": "policy_precheck",
                "command": command,
                "policy_violation": violation,
            },
        )

    def _append_record(self, build_id: UUID, record: RuntimeRunLog) -> None:
        bucket = self._logs[build_id]
        bucket.append(record)
        if len(bucket) > _MAX_LOGS_PER_BUILD:
            del bucket[: len(bucket) - _MAX_LOGS_PER_BUILD]


runner_bridge = RunnerBridge()


def _safe_node_id(node_id: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", node_id).strip("._-")
    return cleaned[:48] or "node"
