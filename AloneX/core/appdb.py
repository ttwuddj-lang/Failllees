import logging
from typing import Optional

import asyncpg

from AloneX import config

logger = logging.getLogger(__name__)


class AppDatabase:
    """Persistent data store for the unified bot.

    This DB is separate from AloneX's MongoDB and can share the existing
    WordSeek PostgreSQL server. All tables use the `unified_` prefix so they
    do not conflict with WordSeek's schema.

    Keep UNIFIED_DATABASE_URL on persistent infrastructure. The bot source
    can then be replaced/upgraded without deleting user/game data.
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if self.pool:
            return
        self.pool = await asyncpg.create_pool(
            dsn=config.UNIFIED_DATABASE_URL,
            min_size=1,
            max_size=5,
            command_timeout=30,
        )
        await self._migrate()
        logger.info("Unified application database connected.")

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def _migrate(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS unified_users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
                );

                CREATE TABLE IF NOT EXISTS unified_game_stats (
                    user_id BIGINT NOT NULL,
                    game TEXT NOT NULL,
                    played BIGINT NOT NULL DEFAULT 0,
                    wins BIGINT NOT NULL DEFAULT 0,
                    losses BIGINT NOT NULL DEFAULT 0,
                    score BIGINT NOT NULL DEFAULT 0,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (user_id, game)
                );

                CREATE TABLE IF NOT EXISTS unified_settings (
                    scope TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (scope, key)
                );

                CREATE INDEX IF NOT EXISTS idx_unified_game_stats_game
                    ON unified_game_stats(game);
            """)

    async def upsert_user(self, user_id: int, username=None, first_name=None):
        if not self.pool:
            return
        await self.pool.execute("""
            INSERT INTO unified_users (user_id, username, first_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                updated_at = NOW()
        """, user_id, username, first_name)

    async def record_game(self, user_id: int, game: str, *,
                          win=False, loss=False, score=0):
        if not self.pool:
            return
        await self.pool.execute("""
            INSERT INTO unified_game_stats
                (user_id, game, played, wins, losses, score)
            VALUES ($1, $2, 1, $3, $4, $5)
            ON CONFLICT (user_id, game) DO UPDATE SET
                played = unified_game_stats.played + 1,
                wins = unified_game_stats.wins + EXCLUDED.wins,
                losses = unified_game_stats.losses + EXCLUDED.losses,
                score = unified_game_stats.score + EXCLUDED.score,
                updated_at = NOW()
        """, user_id, game, int(win), int(loss), score)

    async def get_game_stats(self, user_id: int, game=None):
        if not self.pool:
            return []
        if game:
            row = await self.pool.fetchrow("""
                SELECT game, played, wins, losses, score
                FROM unified_game_stats
                WHERE user_id=$1 AND game=$2
            """, user_id, game)
            return dict(row) if row else None
        rows = await self.pool.fetch("""
            SELECT game, played, wins, losses, score
            FROM unified_game_stats
            WHERE user_id=$1
            ORDER BY score DESC, wins DESC
        """, user_id)
        return [dict(r) for r in rows]

    async def get_setting(self, scope: str, key: str, default=None):
        if not self.pool:
            return default
        row = await self.pool.fetchrow("""
            SELECT value FROM unified_settings
            WHERE scope=$1 AND key=$2
        """, scope, key)
        return row["value"] if row else default

    async def set_setting(self, scope: str, key: str, value):
        if not self.pool:
            return
        await self.pool.execute("""
            INSERT INTO unified_settings(scope, key, value)
            VALUES ($1,$2,$3)
            ON CONFLICT(scope,key) DO UPDATE SET
                value=EXCLUDED.value, updated_at=NOW()
        """, scope, key, str(value))
