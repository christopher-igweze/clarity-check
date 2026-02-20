"""Unit tests for Tier 1 index cache behavior."""

from __future__ import annotations

import unittest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from tier1.indexer import DeterministicIndexer


class Tier1IndexerCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_cache_hit_reuses_existing_index(self) -> None:
        indexer = DeterministicIndexer()
        cached_row = {
            "loc_total": 123,
            "file_count": 4,
            "index_json": {"repo_sha": "abc"},
        }

        with patch("tier1.indexer.db.get_project_index", new=AsyncMock(return_value=cached_row)), patch(
            "tier1.indexer.db.upsert_project_index", new=AsyncMock()
        ) as upsert_mock:
            result = await indexer.build_or_reuse(
                project_id=uuid4(),
                user_id="user_1",
                repo_url="https://github.com/example/repo",
                clone_url="https://github.com/example/repo.git",
                repo_sha="abc",
                github_token=None,
            )

        self.assertTrue(result["cache_hit"])
        self.assertEqual(result["loc_total"], 123)
        upsert_mock.assert_not_called()

    async def test_cache_miss_builds_and_upserts_index(self) -> None:
        indexer = DeterministicIndexer()
        built_index = {
            "repo_sha": "abc",
            "loc_total": 42,
            "file_count": 3,
            "index_json": {"files": []},
        }

        with patch("tier1.indexer.db.get_project_index", new=AsyncMock(return_value=None)), patch(
            "tier1.indexer.asyncio.to_thread", new=AsyncMock(return_value=built_index)
        ), patch("tier1.indexer.db.upsert_project_index", new=AsyncMock()) as upsert_mock:
            result = await indexer.build_or_reuse(
                project_id=uuid4(),
                user_id="user_1",
                repo_url="https://github.com/example/repo",
                clone_url="https://github.com/example/repo.git",
                repo_sha="abc",
                github_token=None,
            )

        self.assertFalse(result["cache_hit"])
        self.assertEqual(result["loc_total"], 42)
        upsert_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
