"""Sandbox command and egress guardrails."""

from __future__ import annotations

import re
from dataclasses import dataclass

DEFAULT_ALLOWED_HOST_SUFFIXES: tuple[str, ...] = (
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "registry.npmjs.org",
    "pypi.org",
    "files.pythonhosted.org",
    "deb.debian.org",
    "security.debian.org",
)

_URL_PATTERN = re.compile(r"https?://([a-zA-Z0-9._-]+)")
_BLOCKED_COMMAND_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-f[dDxX]*\b", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\s+/(?:\s|$)", re.IGNORECASE),
    re.compile(r"\bmkfs\.", re.IGNORECASE),
    re.compile(r"\bshutdown\b", re.IGNORECASE),
    re.compile(r"\breboot\b", re.IGNORECASE),
    re.compile(r"\bpoweroff\b", re.IGNORECASE),
    re.compile(r"\bdd\s+if=.*\s+of=/dev/", re.IGNORECASE),
)


class PolicyViolationError(RuntimeError):
    """Raised when a command violates sandbox safety policy."""

    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class NetworkPolicy:
    allowed_host_suffixes: tuple[str, ...] = DEFAULT_ALLOWED_HOST_SUFFIXES

    def validate_command(self, command: str) -> None:
        normalized = command.strip()
        if not normalized:
            raise PolicyViolationError(
                code="empty_command",
                message="Command is empty.",
            )

        for pattern in _BLOCKED_COMMAND_PATTERNS:
            if pattern.search(normalized):
                raise PolicyViolationError(
                    code="blocked_command",
                    message="Command blocked by sandbox safety policy.",
                )

        for host in _extract_hosts(normalized):
            if not self._is_host_allowed(host):
                raise PolicyViolationError(
                    code="blocked_egress_host",
                    message=f"Command references non-allowlisted host: {host}",
                )

    def _is_host_allowed(self, host: str) -> bool:
        hostname = host.lower().strip(".")
        return any(
            hostname == suffix or hostname.endswith(f".{suffix}")
            for suffix in self.allowed_host_suffixes
        )


def _extract_hosts(command: str) -> set[str]:
    return {match.group(1) for match in _URL_PATTERN.finditer(command)}


DEFAULT_POLICY = NetworkPolicy()

