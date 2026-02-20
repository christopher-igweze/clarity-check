"""Runner bridge that normalizes task execution outcomes for runtime ticks."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import timedelta
from uuid import UUID, uuid4

from models.builds import BuildRun
from models.runtime import RuntimeRunLog, utc_now

_MAX_LOGS_PER_BUILD = 3000

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


def normalize_runner_status(raw_status: object) -> str:
    if not isinstance(raw_status, str):
        return "completed"
    return _STATUS_MAP.get(raw_status.strip().lower(), "completed")


class RunnerBridge:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._logs: dict[UUID, list[RuntimeRunLog]] = defaultdict(list)

    async def execute(
        self,
        *,
        build: BuildRun,
        runtime_id: UUID,
        node_id: str,
    ) -> RuntimeRunLog:
        async with self._lock:
            node_overrides = self._resolve_node_override(build, node_id)
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
    def _normalize_duration(raw: object) -> int:
        if isinstance(raw, int):
            return max(0, raw)
        if isinstance(raw, float):
            return max(0, int(raw))
        return 250

    def _append_record(self, build_id: UUID, record: RuntimeRunLog) -> None:
        bucket = self._logs[build_id]
        bucket.append(record)
        if len(bucket) > _MAX_LOGS_PER_BUILD:
            del bucket[: len(bucket) - _MAX_LOGS_PER_BUILD]


runner_bridge = RunnerBridge()

