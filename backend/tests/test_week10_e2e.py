"""Week 10 e2e: encrypted secret storage and masked secret listing."""

from __future__ import annotations

import unittest
from uuid import uuid4

from e2e_test_app import create_e2e_client, reset_rate_limiter


class Week10E2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = create_e2e_client()

    def setUp(self) -> None:
        reset_rate_limiter()

    def test_store_secret_returns_masked_and_encrypted_metadata(self) -> None:
        user = f"week10-user-{uuid4()}"
        plaintext = "super-secret-token-1234"

        create_resp = self.client.post(
            "/v1/program/week10/secrets",
            json={"name": "github_pat", "value": plaintext},
            headers={"X-Test-User": user},
        )
        self.assertEqual(create_resp.status_code, 200)
        secret = create_resp.json()
        self.assertEqual(secret["name"], "github_pat")
        self.assertNotEqual(secret["masked_value"], plaintext)
        self.assertEqual(len(secret["cipher_digest"]), 16)

        list_resp = self.client.get(
            "/v1/program/week10/secrets",
            headers={"X-Test-User": user},
        )
        self.assertEqual(list_resp.status_code, 200)
        listed = list_resp.json()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["masked_value"], "***")
        self.assertNotIn(plaintext, str(listed))

        meta_resp = self.client.get(
            f"/v1/program/week10/secrets/{secret['secret_id']}",
            headers={"X-Test-User": user},
        )
        self.assertEqual(meta_resp.status_code, 200)
        metadata = meta_resp.json()
        self.assertGreater(metadata["cipher_length"], len(plaintext))


if __name__ == "__main__":
    unittest.main()

