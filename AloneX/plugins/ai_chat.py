# Unified AI chat integration from Aichatbiit.
# This replaces Aichatbiit's python-telegram-bot polling loop with a native
# Pyrogram handler so the combined project uses one Telegram bot identity.

import os

from groq import Groq
from pyrogram import filters, types

from AloneX import app

_GROQ_KEY = os.getenv("GROQ_API_KEY", "").strip()
_client = Groq(api_key=_GROQ_KEY) if _GROQ_KEY else None

_SYSTEM = (
    "You are Ada. Sabse friendly tareeke se baat karo. "
    "Hindi me baat karo lekin English alphabets me. "
    "Short aur natural replies do. User jaise baat kare waise reply do. "
    "Human friend ki tarah behave karo."
)


async def _reply_ai(message: types.Message, prompt: str):
    if not _client:
        return await message.reply_text(
            "⚠️ GROQ_API_KEY configured nahi hai."
        )

    try:
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        reply = response.choices[0].message.content or "⚠️ Empty response."
        await message.reply_text(reply[:4000])
    except Exception:
        await message.reply_text(
            "⚠️ AI busy hai, thodi der baad try karo."
        )


@app.on_message(filters.command(["ai", "ask"]) & ~app.bl_users)
async def ai_command(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /ai <message>")
    await _reply_ai(message, " ".join(message.command[1:]))


@app.on_message(
    filters.text
    & ~filters.command(["start", "help", "play"])
    & ~app.bl_users
)
async def ai_text(_, message: types.Message):
    # In groups, only answer when the user replies to the bot.
    if message.chat.type in ("group", "supergroup"):
        reply = message.reply_to_message
        if not reply or not reply.from_user or reply.from_user.id != app.id:
            return

    text = message.text.strip()
    if not text:
        return
    await _reply_ai(message, text)
