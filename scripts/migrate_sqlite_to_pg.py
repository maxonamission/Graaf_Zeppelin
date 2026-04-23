#!/usr/bin/env python3
"""Migrate data from SQLite to PostgreSQL.

Usage:
    python scripts/migrate_sqlite_to_pg.py \
        --sqlite sqlite+aiosqlite:///./graaf_zeppelin.db \
        --pg postgresql+asyncpg://user:pass@host/graaf_zeppelin

This script:
1. Reads all data from SQLite
2. Creates tables in PostgreSQL (if they don't exist)
3. Inserts all data into PostgreSQL
4. Reports migration statistics
"""

import argparse
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import all models to register metadata
from app.models import DailyUsage, License, Release, User, UserApiKey  # noqa: F401
from app.models.base import Base
from app.models.conversation import Conversation, Message  # noqa: F401

TABLES = [
    "licenses",
    "users",
    "releases",
    "conversations",
    "messages",
    "daily_usage",
    "user_api_keys",
]


async def migrate(sqlite_url: str, pg_url: str) -> None:
    """Copy all data from SQLite to PostgreSQL."""
    sqlite_engine = create_async_engine(sqlite_url)
    pg_engine = create_async_engine(pg_url)

    # Create tables in PostgreSQL
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sqlite_session = async_sessionmaker(sqlite_engine, class_=AsyncSession)
    pg_session = async_sessionmaker(pg_engine, class_=AsyncSession)

    stats = {}

    for table_name in TABLES:
        async with sqlite_session() as src:
            result = await src.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.mappings().all()

        if not rows:
            stats[table_name] = 0
            continue

        columns = list(rows[0].keys())
        col_list = ", ".join(columns)
        param_list = ", ".join(f":{c}" for c in columns)

        async with pg_session() as dst:
            for row in rows:
                await dst.execute(
                    text(f"INSERT INTO {table_name} ({col_list}) VALUES ({param_list})"),
                    dict(row),
                )
            await dst.commit()

        stats[table_name] = len(rows)

    await sqlite_engine.dispose()
    await pg_engine.dispose()

    print("\n=== Migratie voltooid ===")
    for table, count in stats.items():
        print(f"  {table}: {count} rijen")
    print(f"\nTotaal: {sum(stats.values())} rijen gemigreerd")


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite to PostgreSQL")
    parser.add_argument("--sqlite", required=True, help="SQLite connection URL")
    parser.add_argument("--pg", required=True, help="PostgreSQL connection URL")
    args = parser.parse_args()
    asyncio.run(migrate(args.sqlite, args.pg))


if __name__ == "__main__":
    main()
