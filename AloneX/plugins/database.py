from pyrogram import filters, types
from AloneX import app, appdb

@app.on_message(filters.command("mystats"))
async def my_stats(_, m: types.Message):
    await appdb.upsert_user(
        m.from_user.id,
        m.from_user.username,
        m.from_user.first_name,
    )
    stats = await appdb.get_game_stats(m.from_user.id)
    if not stats:
        return await m.reply_text(
            "📊 **Your stats**\n\nNo game stats yet. Start playing!"
        )
    lines = ["📊 **Your persistent game stats**", ""]
    for row in stats:
        lines.append(
            f"🎮 {row['game']}: {row['played']} played • "
            f"{row['wins']} wins • {row['losses']} losses • "
            f"{row['score']} points"
        )
    await m.reply_text("\n".join(lines))
