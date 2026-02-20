"""Command execution abstraction for Daytona sandboxes."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from daytona import Sandbox

from sandbox.network_policy import DEFAULT_POLICY, NetworkPolicy


@dataclass
class CommandResult:
    """Normalised result of a command execution inside a sandbox."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int = 0


class SandboxExecutor:
    """Executes commands with fail-closed policy enforcement."""

    def __init__(self, policy: NetworkPolicy | None = None) -> None:
        self._policy = policy or DEFAULT_POLICY

    async def execute(
        self,
        *,
        sandbox: Sandbox,
        command: str,
        cwd: str,
        timeout: int = 120,
    ) -> CommandResult:
        self._policy.validate_command(command)

        outer_timeout = max(30, int(timeout) + 30)
        try:
            resp = await asyncio.wait_for(
                asyncio.to_thread(
                    sandbox.process.exec,
                    command,
                    cwd=cwd,
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

