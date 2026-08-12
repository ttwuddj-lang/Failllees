"""Native WordSeek mini-game for the unified Pyrogram bot.

This is intentionally self-contained so it does not start another Telegram bot.
The original TypeScript WordSeek project remains in /wordseek as a reference/
advanced implementation, while this plugin provides a working in-bot game.
"""

import random
from AloneX import app, appdb
from pyrogram import filters, types

_WORDS = [
    "apple","brave","chair","cloud","dance","dream","eagle","earth","flame",
    "grape","green","house","human","lemon","light","magic","music","ocean",
    "paper","plant","queen","river","robot","school","snake","space","stone",
    "table","tiger","train","water","world","zebra","alone","artist","brain",
    "bread","break","candy","crown","field","flower","friend","garden","happy",
    "heart","horse","island","jungle","keyboard","little","market","orange",
    "phone","planet","purple","rainbow","silver","summer","winter",
]

_ACTIVE = {}

def _new_word():
    return random.choice(_WORDS)

def _mask(secret, guess):
    out = []
    for i, ch in enumerate(guess):
        if i < len(secret) and ch == secret[i]:
            out.append("🟩")
        elif ch in secret:
            out.append("🟨")
        else:
            out.append("⬛")
    return " ".join(out)

@app.on_message(filters.command("wordseek"))
async def wordseek_start(_, m: types.Message):
    secret = _new_word()
    _ACTIVE[m.chat.id] = {"word": secret, "tries": 0, "max": 6}
    await appdb.upsert_user(m.from_user.id, m.from_user.username, m.from_user.first_name)
    await m.reply_text(
        "🔤 **WordSeek started!**\n\n"
        "Guess the hidden 5-letter word.\n"
        "🟩 correct position  🟨 wrong position  ⬛ not present\n"
        "You have 6 tries.\n\n"
        "Use `/guessword <word>`"
    )

@app.on_message(filters.command("guessword"))
async def wordseek_guess(_, m: types.Message):
    game = _ACTIVE.get(m.chat.id)
    if not game:
        return await m.reply_text("Start a game with `/wordseek`.")
    if len(m.command) < 2:
        return await m.reply_text("Use `/guessword <5-letter-word>`.")
    guess = m.command[1].lower().strip()
    if len(guess) != 5 or not guess.isalpha():
        return await m.reply_text("Please enter exactly 5 letters.")
    game["tries"] += 1
    secret = game["word"]
    result = _mask(secret, guess)
    if guess == secret:
        _ACTIVE.pop(m.chat.id, None)
        await appdb.record_game(m.from_user.id, "wordseek", win=True, score=10)
        return await m.reply_text(
            f"🎉 **Correct!** `{guess}`\n{result}\n\n🏆 +10 points"
        )
    if game["tries"] >= game["max"]:
        _ACTIVE.pop(m.chat.id, None)
        await appdb.record_game(m.from_user.id, "wordseek", loss=True)
        return await m.reply_text(
            f"{result}\n\n❌ Game over. The word was **{secret}**."
        )
    await m.reply_text(
        f"`{guess}`\n{result}\n\n"
        f"Attempts: {game['tries']}/{game['max']}"
    )

@app.on_message(filters.command("wordseekstats"))
async def wordseek_stats(_, m: types.Message):
    row = await appdb.get_game_stats(m.from_user.id, "wordseek")
    if not row:
        return await m.reply_text("No WordSeek stats yet. Play `/wordseek`.")
    await m.reply_text(
        "📊 **WordSeek Stats**\n\n"
        f"Played: {row['played']}\n"
        f"Wins: {row['wins']}\n"
        f"Losses: {row['losses']}\n"
        f"Score: {row['score']}"
    )
