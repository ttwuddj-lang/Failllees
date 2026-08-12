# UnifiedAloneX features

This build runs the features inside the existing AloneX Pyrogram process.

Commands:
- `/features` — unified feature menu
- `/games` — games list
- `/wordseek` or `/ws` — native WordSeek
- `/wsstats` — WordSeek persistent stats
- `/wordchain` — Word Chain lobby
- `/uno` — UNO
- `/ai <message>` / `/ask <message>` — AI chat

Required Railway variables include `GROQ_API_KEY` for AI and the existing Telegram/Mongo/PostgreSQL variables.

The original `wordseek/` source remains in the repository for reference; Railway does not need to start it as a second bot process.
