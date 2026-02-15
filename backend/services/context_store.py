"""Shared context store for passing data between agents without token bloat.

Instead of re-streaming raw file content through every agent's chat history,
the orchestrator saves artifacts (file contents, findings, probe results) into
this store.  Downstream agents receive *references* and can pull the data they
need on demand, keeping prompt sizes small.
"""

from __future__ import annotations

import threading
from typing import Any
from uuid import UUID


class ContextStore:
    """Thread-safe key/value store scoped to a single scan session.

    Keys follow a namespace convention:
        file:<path>         — raw file content
        tree                — repo file tree listing
        findings:scanner    — Scanner agent's raw findings
        findings:security   — Security agent's validated findings
        probe:results       — Builder agent's dynamic probe results
        plan:actions        — Planner agent's action items
        education:cards     — Educator agent's cards
        charter             — Project charter from vision intake
    """

    def __init__(self, scan_id: UUID) -> None:
        self.scan_id = scan_id
        self._data: dict[str, Any] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def get_all(self, prefix: str) -> dict[str, Any]:
        """Return all entries whose key starts with *prefix*."""
        with self._lock:
            return {k: v for k, v in self._data.items() if k.startswith(prefix)}

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._data.keys())

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
