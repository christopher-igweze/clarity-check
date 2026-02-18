"""Manual cleanup helper for expired Tier 1 artifacts and indexes."""

from __future__ import annotations

import asyncio

from services import supabase_client as db


async def main() -> None:
    deleted_artifacts = await db.delete_expired_report_artifacts()
    deleted_indexes = await db.delete_expired_project_indexes()
    print(f"deleted_report_artifacts={deleted_artifacts}")
    print(f"deleted_project_indexes={deleted_indexes}")


if __name__ == "__main__":
    asyncio.run(main())
