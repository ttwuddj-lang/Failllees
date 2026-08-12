from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AloneX import app, config

@app.on_message(filters.command(["features","menu"]))
async def unified_menu(_, m: types.Message):
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Games", callback_data="unified_games"),
         InlineKeyboardButton("🔤 WordSeek", callback_data="unified_wordseek")],
        [InlineKeyboardButton("💬 AI Chat", callback_data="unified_ai"),
         InlineKeyboardButton("🔗 Support", url=config.SUPPORT_CHANNEL)],
        [InlineKeyboardButton("📦 Repository", url="https://github.com/w1899222-droid/JpBiggestprogram")],
    ])
    await m.reply_text(
        "✨ **Unified Bot Features**\n\n"
        "🎵 Music + Voice Chat\n"
        "🤖 AI Chat — `/ai your message`\n"
        "🔤 WordSeek — `/wordseek`\n"
        "🔗 Word Chain — `/wordchain`\n"
        "🃏 UNO — `/uno`\n"
        "🎮 Mini Games — `/games`\n\n"
        "Use the buttons below:",
        reply_markup=kb,
    )

@app.on_callback_query(filters.regex("^unified_"))
async def unified_callback(_, q: types.CallbackQuery):
    action=q.data
    if action=="unified_games":
        text=("🎮 **Games**\n\n"
              "/quiz /trivia\n/ttt\n/rps rock\n/number\n/hangman\n"
              "/memory\n/dice\n/coin\n/uno\n/wordchain\n/wordseek")
    elif action=="unified_wordseek":
        text="🔤 **WordSeek**\n\n`/wordseek` to start.\n`/ws apple` to guess."
    elif action=="unified_ai":
        text="💬 **AI Chat**\n\nUse `/ai <message>` or `/ask <message>`."
    else:
        text="Use `/features` to open the feature menu."
    await q.answer()
    await q.message.reply_text(text)
