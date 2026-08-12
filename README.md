# Unified AloneX + AI Chat + WordSeek

This repository combines the three uploaded codebases into one deployable project.

## What is integrated

- **AloneX** remains the main Pyrogram music/voice-chat bot.
- **Aichatbiit AI chat** is integrated as native Pyrogram handlers:
  - `/ai <message>`
  - `/ask <message>`
  - In groups, normal text is answered only when replying to the bot.
- **WordSeek** remains its original Bun/TypeScript service and uses the **same `BOT_TOKEN`**.
- The original Aichatbiit source is preserved under `legacy/Aichatbiit/`.

## Important architecture note

AloneX uses Pyrogram/MTProto while WordSeek uses grammY/Telegram Bot API. They are separate client runtimes but are configured with the same bot token. This avoids running two Bot API `getUpdates` consumers. If your deployment/provider rejects simultaneous MTProto + Bot API use for the same bot, WordSeek must be ported into the Pyrogram layer or run with a second bot token.

The Aichatbiit original `python-telegram-bot` polling loop is **not started**; its AI logic was ported to `AloneX/plugins/ai_chat.py` so it does not create a second Bot API polling consumer.

## Setup

1. Copy `.env.example` to `.env`.
2. Fill:
   - `BOT_TOKEN`
   - `API_ID`
   - `API_HASH`
   - `MONGO_URL`
   - `LOGGER_ID`
   - `OWNER_ID`
   - `SESSION`
   - `GROQ_API_KEY`
   - WordSeek `DATABASE_URL`, `REDIS_URI`, `DAILY_WORDLE_SECRET`
3. Install Python requirements:
   `pip install -r requirements.txt`
4. Install Bun dependencies:
   `cd wordseek && bun install && cd ..`
5. Start everything:
   `bash start-all.sh`

## Docker

```bash
cp .env.example .env
docker compose up -d --build
```

For Docker, use these database values in `.env`:
- `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/wordseek`
- `REDIS_URI=redis://redis:6379`

## Termux / VPS

The project expects Python 3, Bun, FFmpeg and the services required by the original projects. A VPS is recommended for the music/voice features.

## Files

- `AloneX/` - original AloneX music bot
- `config.py` - AloneX configuration
- `wordseek/` - original WordSeek application
- `legacy/Aichatbiit/` - original Aichatbiit source
- `AloneX/plugins/ai_chat.py` - integrated AI feature
- `.env.example` - combined environment template
- `start-all.sh` - starts both bot runtimes
- `docker-compose.yml` - PostgreSQL + Redis + combined bot

## Security

Do not commit `.env`, bot tokens, API keys, database passwords or Telegram session strings.


## Added Mini-Games

The combined bot now includes: `/games`, `/quiz`, `/trivia`, `/ttt`, `/rps`, `/number`, `/guess`, `/hangman`, `/letter`, `/memory`, `/memoryanswer`, `/dice`, and `/coin`.
Game state is in-memory and resets when the bot restarts.

## UNO

Added multiplayer UNO commands: `/uno`, `/unojoin`, `/unoleave`, `/unostart`, `/unoplay`, `/unodraw`, `/unocolor`, `/unostatus`.

## UNO Card Stickers

UNO cards are bundled as WebP sticker-style assets under `assets/uno_stickers/`. Played and drawn cards are sent as stickers with a text fallback.

## UNO Screenshot-Style UI

UNO now renders a game-board image showing the top card and hand, with inline card-choice buttons and a Draw button. This is designed to resemble the supplied UNO bot screenshot.

## Word Chain

Added an integrated Word Chain game adapted for the existing Pyrogram bot. The supplied on9wordchainbot source is preserved under `legacy/on9wordchainbot/`; it is not started as a second Telegram bot. Commands: `/wordchain`, `/wcjoin`, `/wcleave`, `/wcstart`, `/wcstatus`, `/wcstop`. Players then send 4–6 letter English words directly in the group; each word must start with the last letter of the previous word and cannot be reused. The bundled dictionary is built from the existing WordSeek common 4/5/6-letter lists.

## Persistent Database System

A dedicated `AppDatabase` layer has been added for data that should survive code/file updates:

- PostgreSQL-backed `unified_users`
- `unified_game_stats`
- `unified_settings`
- automatic table migration on startup
- `/mystats` for persistent game statistics
- `scripts/backup-db.sh` and `scripts/restore-db.sh`

Set `UNIFIED_DATABASE_URL` to a persistent PostgreSQL database. It can use the same PostgreSQL server/database as WordSeek because all unified tables are prefixed with `unified_`.

### Important deployment rule

**Do not keep your production database inside the source ZIP/repository.** Put PostgreSQL on a persistent volume/service (Railway PostgreSQL, Supabase, Neon, a VPS volume, or Docker's named volume). You can then replace/update the bot source without deleting user data.

For Docker, the included `postgres` service uses a named volume (`wordseek_pg`), so recreating the bot container does not delete the PostgreSQL data.

Before updating source files, make a backup:

```bash
./scripts/backup-db.sh
```

After a failed update, restore if necessary:

```bash
./scripts/restore-db.sh db_backups/unified_YYYYMMDD_HHMMSS.dump
```

**Note:** active in-memory game rounds (for example an UNO round currently being played) still reset if the process crashes/restarts. Persistent user/settings/stats data survives. Making every active game resumable would require a second persistence pass for each game's state.
