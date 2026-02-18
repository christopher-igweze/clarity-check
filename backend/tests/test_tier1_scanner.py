"""Unit tests for Tier 1 deterministic scanner contract."""

from __future__ import annotations

import unittest

from tier1.scanner import DeterministicScanner


class Tier1ScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scanner = DeterministicScanner()

    def _base_payload(self) -> dict:
        return {
            "index_json": {
                "signals": {
                    "secret_matches": [],
                    "private_key_matches": [],
                    "insecure_cors_matches": [],
                    "dangerous_exec_matches": [],
                    "sql_matches": [],
                    "route_hints": [],
                    "env_usage": [],
                    "weak_error_logging": [],
                    "blocking_sync": [],
                },
                "facts": {
                    "has_ci": True,
                    "has_tests": True,
                    "has_env_example": True,
                    "tracked_env_files": [],
                    "manifests_present": ["package.json"],
                    "lockfiles_present": ["package-lock.json"],
                },
                "files": [
                    {"path": "src/app.ts", "loc": 120, "ext": ".ts", "sha256": "x", "path_role": "source"},
                ],
                "linter_probes": [],
            }
        }

    def _check(self, findings, check_id: str):
        for finding in findings:
            if finding.check_id == check_id:
                return finding
        self.fail(f"Missing check {check_id}")

    def test_security_fixture_flags_hardcoded_secret(self) -> None:
        payload = self._base_payload()
        payload["index_json"]["signals"]["secret_matches"] = [
            {
                "file_path": "src/config.ts",
                "line_number": 12,
                "snippet": "const key = 'AKIA1234567890ABCD12'",
                "match": "aws_access_key",
            }
        ]

        findings = self.scanner.scan(index_payload=payload, sensitive_data=[])
        sec = self._check(findings, "SEC_001")
        self.assertEqual(sec.status, "fail")
        self.assertEqual(sec.category, "security")

    def test_reliability_fixture_flags_missing_tests(self) -> None:
        payload = self._base_payload()
        payload["index_json"]["facts"]["has_tests"] = False

        findings = self.scanner.scan(index_payload=payload, sensitive_data=[])
        rel = self._check(findings, "REL_001")
        self.assertEqual(rel.status, "fail")
        self.assertEqual(rel.category, "reliability")

    def test_scalability_fixture_flags_large_file(self) -> None:
        payload = self._base_payload()
        payload["index_json"]["files"] = [
            {"path": "backend/huge.py", "loc": 920, "ext": ".py", "sha256": "x", "path_role": "backend"},
            {"path": "src/app.ts", "loc": 80, "ext": ".ts", "sha256": "y", "path_role": "source"},
        ]

        findings = self.scanner.scan(index_payload=payload, sensitive_data=[])
        scl = self._check(findings, "SCL_001")
        self.assertEqual(scl.status, "fail")
        self.assertEqual(scl.severity, "high")

    def test_scalability_ignores_large_lockfile(self) -> None:
        payload = self._base_payload()
        payload["index_json"]["files"] = [
            {"path": "package-lock.json", "loc": 25000, "ext": ".json", "sha256": "x", "path_role": "config"},
            {"path": "src/app.ts", "loc": 120, "ext": ".ts", "sha256": "y", "path_role": "source"},
        ]

        findings = self.scanner.scan(index_payload=payload, sensitive_data=[])
        scl = self._check(findings, "SCL_001")
        self.assertEqual(scl.status, "pass")
        self.assertEqual(len(scl.evidence), 0)


if __name__ == "__main__":
    unittest.main()
