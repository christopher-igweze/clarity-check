"""Daytona sandbox lifecycle manager.

Provisions ephemeral Docker sandboxes for each audit session.  Agents
clone repos, run commands, and inspect output inside these sandboxes.
Sandboxes auto-delete after ``sandbox_timeout_minutes`` of inactivity.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from uuid import UUID

from daytona import (
    Daytona,
    DaytonaConfig,
    CreateSandboxFromImageParams,
    Image,
    Resources,
    Sandbox,
)

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Normalised result of a command execution inside a sandbox."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int = 0


@dataclass
class SandboxSession:
    """Tracks a live sandbox and its associated scan."""

    scan_id: UUID
    sandbox: Sandbox
    repo_path: str = "/home/daytona/repo"


class SandboxManager:
    """Creates, manages, and tears down Daytona sandboxes."""

    def __init__(self) -> None:
        # NOTE: If target is None, Daytona will pick the org default.
        # Passing an unsupported target yields errors like:
        # "Region us is not available to the organization".
        target = settings.daytona_target or None
        if isinstance(target, str) and not target.strip():
            target = None
        config = DaytonaConfig(
            api_key=settings.daytona_api_key,
            api_url=settings.daytona_api_url,
            target=target,
        )
        self._daytona = Daytona(config)
        self._sessions: dict[UUID, SandboxSession] = {}

    async def provision(self, scan_id: UUID, clone_url: str) -> SandboxSession:
        """Spin up a sandbox, clone the repo, and return a session handle."""
        logger.info("Provisioning sandbox for scan %s", scan_id)

        image = (
            Image.debian_slim("3.12")
            .pip_install(["semgrep"])
            .workdir("/home/daytona")
        )

        sandbox = self._daytona.create(
            CreateSandboxFromImageParams(
                image=image,
                resources=Resources(
                    cpu=settings.sandbox_cpu,
                    memory=settings.sandbox_memory_gb,
                    disk=settings.sandbox_disk_gb,
                ),
                auto_stop_interval=settings.sandbox_timeout_minutes,
                ephemeral=True,
                labels={"scan_id": str(scan_id)},
                env_vars={"SCAN_ID": str(scan_id)},
            ),
        )

        repo_path = "/home/daytona/repo"
        sandbox.git.clone(clone_url, repo_path)

        session = SandboxSession(
            scan_id=scan_id, sandbox=sandbox, repo_path=repo_path
        )
        self._sessions[scan_id] = session
        logger.info("Sandbox ready for scan %s", scan_id)
        return session

    async def exec(
        self, scan_id: UUID, command: str, cwd: str | None = None, timeout: int = 120
    ) -> CommandResult:
        """Execute a command inside the scan's sandbox."""
        session = self._sessions.get(scan_id)
        if session is None:
            raise RuntimeError(f"No sandbox session for scan {scan_id}")

        work_dir = cwd or session.repo_path
        # The Daytona SDK exec call is synchronous and can occasionally block on HTTP response
        # reads even after the remote command has completed. Run it off-thread with an outer
        # asyncio timeout to avoid hanging the whole orchestration loop indefinitely.
        outer_timeout = max(30, int(timeout) + 30)

        try:
            resp = await asyncio.wait_for(
                asyncio.to_thread(
                    session.sandbox.process.exec,
                    command,
                    cwd=work_dir,
                    timeout=timeout,
                ),
                timeout=outer_timeout,
            )
        except asyncio.TimeoutError as exc:
            raise RuntimeError(
                f"Sandbox exec response timeout after {outer_timeout}s for command: {command[:120]}"
            ) from exc

        return CommandResult(
            command=command,
            exit_code=resp.exit_code,
            stdout=resp.result or "",
            stderr="",
        )

    async def read_file(self, scan_id: UUID, path: str) -> str:
        """Download a file's contents from the sandbox."""
        session = self._sessions.get(scan_id)
        if session is None:
            raise RuntimeError(f"No sandbox session for scan {scan_id}")
        try:
            content = session.sandbox.fs.download_file(path)
            return content.decode("utf-8", errors="replace")
        except Exception as exc:
            logger.warning("download_file failed for %s: %s; falling back to cat", path, exc)
            result = await self.exec(scan_id, f"cat {path}", cwd="/home/daytona", timeout=120)
            if result.exit_code != 0:
                raise RuntimeError(f"Failed to read file via fallback cat: {path}")
            return result.stdout

    async def upload_file(self, scan_id: UUID, path: str, content: bytes) -> None:
        """Upload a file into the sandbox."""
        session = self._sessions.get(scan_id)
        if session is None:
            raise RuntimeError(f"No sandbox session for scan {scan_id}")
        session.sandbox.fs.upload_file(content, path)

    async def get_file_tree(self, scan_id: UUID) -> str:
        """Return a recursive listing of the repo directory."""
        result = await self.exec(
            scan_id,
            "find . -type f -not -path './.git/*' -not -path './node_modules/*' | head -500 | sort",
        )
        return result.stdout

    async def destroy(self, scan_id: UUID) -> None:
        """Tear down the sandbox for a scan."""
        session = self._sessions.pop(scan_id, None)
        if session is None:
            return
        try:
            session.sandbox.delete()
            logger.info("Sandbox destroyed for scan %s", scan_id)
        except Exception:
            logger.exception("Failed to destroy sandbox for scan %s", scan_id)
