"""Tests for durable ProgramStore snapshot loading."""

from __future__ import annotations

import os
import tempfile
import unittest

# Ensure config.Settings can initialize during imports in test environments.
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("DAYTONA_API_KEY", "test")

from models.program import (  # noqa: E402
    PolicyProfileRequest,
    ReleaseChecklistRequest,
    RollbackDrillRequest,
    SecretCreateRequest,
    ValidationCampaignRequest,
)
from orchestration.program_store import ProgramStore  # noqa: E402


class ProgramStorePersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_persists_and_restores_core_program_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "program-store.json")
            store = ProgramStore(state_path=state_path)

            campaign = await store.create_campaign(
                user_id="u1",
                request=ValidationCampaignRequest(
                    name="camp",
                    repos=["repo-a", "repo-b"],
                    runs_per_repo=3,
                ),
            )
            profile = await store.create_policy_profile(
                user_id="u1",
                request=PolicyProfileRequest(
                    name="strict",
                    blocked_commands=["rm -rf"],
                    restricted_paths=["/.git"],
                ),
            )
            secret = await store.store_secret(
                user_id="u1",
                request=SecretCreateRequest(name="token", value="plain-text-token"),
            )
            checklist = await store.upsert_release_checklist(
                user_id="u1",
                request=ReleaseChecklistRequest(
                    release_id="r1",
                    security_review=True,
                    slo_dashboard=True,
                    rollback_tested=False,
                    docs_complete=True,
                    runbooks_ready=True,
                ),
            )
            await store.upsert_rollback_drill(
                user_id="u1",
                request=RollbackDrillRequest(
                    release_id="r1",
                    passed=True,
                    duration_minutes=9,
                    issues_found=[],
                ),
            )

            reloaded = ProgramStore(state_path=state_path)
            restored_campaign = await reloaded.get_campaign(campaign.campaign_id)
            self.assertIsNotNone(restored_campaign)
            self.assertEqual(restored_campaign.name, "camp")

            restored_profile = await reloaded.get_policy_profile(profile.profile_id)
            self.assertIsNotNone(restored_profile)
            self.assertIn("rm -rf", restored_profile.blocked_commands)

            listed_secrets = await reloaded.list_secrets(user_id="u1")
            self.assertEqual(len(listed_secrets), 1)
            self.assertEqual(listed_secrets[0].secret_id, secret.secret_id)

            secret_meta = await reloaded.get_secret_metadata(secret_id=secret.secret_id, user_id="u1")
            self.assertGreater(secret_meta.cipher_length, 10)

            restored_checklist = await reloaded.get_release_checklist("r1")
            self.assertIsNotNone(restored_checklist)
            self.assertEqual(restored_checklist.release_id, checklist.release_id)


if __name__ == "__main__":
    unittest.main()

