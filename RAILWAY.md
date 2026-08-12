# Railway deployment

1. Upload the contents of this folder to the root of a GitHub repository.
2. In Railway, create a project and choose **Deploy from GitHub Repo**.
3. Add a **PostgreSQL** service.
4. In the bot service Variables, set:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
   - `OWNER_ID`
   - `LOGGER_ID`
   - `MONGO_URL` (if Mongo-backed features are enabled)
   - `REDIS_URL` (if Redis-backed features are enabled)
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `UNIFIED_DATABASE_URL=${{Postgres.DATABASE_URL}}`
5. The included `railway.toml` starts the bot with:
   `python3 -m AloneX`
6. Redeploy after saving Variables.

Do not commit `.env`, tokens, API keys, or database dumps.

The PostgreSQL service should remain separate from the bot service so source-code redeploys do not delete persistent database data.
