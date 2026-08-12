"""
Word Chain game adapted from the supplied on9wordchainbot project.

This module is intentionally integrated into the existing Pyrogram bot rather
than starting a second Telegram bot. The original source is preserved under
legacy/on9wordchainbot/.
"""

import asyncio
import json
import os
import random
import re
from pyrogram import filters, types
from AloneX import app

_WC = {}

_WORD_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets", "wordchain", "words.json"
)
try:
    with open(_WORD_FILE, encoding="utf-8") as f:
        _WC_WORDS = set(json.load(f))
except Exception:
    _WC_WORDS = {
        "apple","about","alone","along","angle","animal","answer","artist",
        "banana","basic","black","board","brain","bread","break","bring",
        "chair","chain","change","child","class","cloud","dance","dream",
        "earth","eagle","early","every","family","field","first","flower",
        "game","green","group","happy","house","human","image","light",
        "magic","music","night","ocean","paper","phone","place","plant",
        "queen","quick","river","school","small","snake","sound","space",
        "start","stone","table","tiger","train","water","world","young"
    }

def _wc_key(m):
    return m.chat.id

def _wc_name(user):
    return user.first_name or user.username or str(user.id)

def _wc_state(chat_id):
    return _WC.get(chat_id)

def _wc_pick_start():
    return random.choice(tuple(_WC_WORDS))

def _wc_render(g):
    players = g["players"]
    turn = players[g["turn"]][1] if players else "—"
    last = g["last_word"] or "—"
    scores = "\n".join(
        f"{i+1}. {name} — {score}"
        for i, (_, name, score) in enumerate(
            sorted(players, key=lambda x: (-x[2], x[0]))
        )
    ) or "No players"
    return (
        "🔗 **Word Chain**\n\n"
        f"Last word: **{last}**\n"
        f"Next letter: **{g['required']}**\n"
        f"Turn: **{turn}**\n\n"
        f"🏆 **Scores**\n{scores}\n\n"
        "Send a word directly in the group when it is your turn."
    )

@app.on_message(filters.command("wordchain"))
async def wc_create(_, m: types.Message):
    k=_wc_key(m)
    if m.chat.type.value not in ("group","supergroup"):
        return await m.reply_text("🔗 Word Chain is designed for groups.")
    if k in _WC:
        return await m.reply_text("A Word Chain game is already running here. Use /wcstatus.")
    _WC[k]={
        "players": [],
        "turn": 0,
        "last_word": "",
        "required": "",
        "used": set(),
        "running": False,
        "min_len": 4,
        "max_players": 50,
        "turn_task": None,
        "deadline": 0,
    }
    await m.reply_text(
        "🔗 **Word Chain game created!**\n\n"
        "Join with `/wcjoin`.\n"
        "Start with `/wcstart` when everyone has joined.\n\n"
        "Rules: your word must begin with the required letter, "
        "be 4–6 letters long, and not have been used before."
    )

@app.on_message(filters.command("wcjoin"))
async def wc_join(_, m: types.Message):
    k=_wc_key(m)
    g=_wc_state(k)
    if not g:
        return await m.reply_text("Create a game with /wordchain.")
    if g["running"]:
        return await m.reply_text("The game has already started.")
    pid=m.from_user.id
    if any(p[0]==pid for p in g["players"]):
        return await m.reply_text("You already joined.")
    if len(g["players"]) >= g["max_players"]:
        return await m.reply_text("The game is full.")
    g["players"].append((pid,_wc_name(m.from_user),0))
    await m.reply_text(f"✅ {_wc_name(m.from_user)} joined. Players: {len(g['players'])}")

@app.on_message(filters.command("wcleave"))
async def wc_leave(_, m: types.Message):
    k=_wc_key(m); g=_wc_state(k)
    if not g:
        return await m.reply_text("No Word Chain game here.")
    if g["running"]:
        return await m.reply_text("You can't leave during a running round. Use /wcstop if you're the game creator.")
    pid=m.from_user.id
    g["players"]=[p for p in g["players"] if p[0]!=pid]
    await m.reply_text("You left the Word Chain lobby.")

@app.on_message(filters.command("wcstart"))
async def wc_start(_, m: types.Message):
    k=_wc_key(m); g=_wc_state(k)
    if not g:
        return await m.reply_text("Create a game with /wordchain.")
    if g["running"]:
        return await m.reply_text("Game already started.")
    if len(g["players"]) < 2:
        return await m.reply_text("At least 2 players are required.")
    g["running"]=True
    g["turn"]=0
    start=_wc_pick_start()
    g["last_word"]=start
    g["required"]=start[-1]
    g["used"]={start}
    await m.reply_text(
        "🔗 **Word Chain started!**\n\n"
        f"Starting word: **{start}**\n"
        f"First turn: **{g['players'][0][1]}**\n"
        f"Next word must start with **{g['required'].upper()}**.\n\n"
        "Type your word directly in the group."
    )

@app.on_message(filters.command("wcstatus"))
async def wc_status(_, m: types.Message):
    g=_wc_state(_wc_key(m))
    if not g:
        return await m.reply_text("No Word Chain game here.")
    await m.reply_text(_wc_render(g))

@app.on_message(filters.command("wcstop"))
async def wc_stop(_, m: types.Message):
    k=_wc_key(m); g=_wc_state(k)
    if not g:
        return await m.reply_text("No Word Chain game here.")
    # Keep this simple: only a player can stop the game.
    if not any(p[0]==m.from_user.id for p in g["players"]):
        return await m.reply_text("Only a player can stop this game.")
    _WC.pop(k,None)
    await m.reply_text("🛑 Word Chain game stopped.")

async def _wc_timeout(chat_id):
    await asyncio.sleep(40)
    g=_wc_state(chat_id)
    if not g or not g["running"]:
        return
    if asyncio.get_running_loop().time() < g["deadline"]:
        return
    pid,name,score=g["players"][g["turn"]]
    await app.send_message(chat_id, f"⏰ {name} ran out of time. Turn skipped.")
    g["turn"]=(g["turn"]+1)%len(g["players"])
    g["deadline"]=asyncio.get_running_loop().time()+40
    g["turn_task"]=asyncio.create_task(_wc_timeout(chat_id))
    await app.send_message(chat_id, _wc_render(g))

@app.on_message(filters.text & ~filters.command([
    "start","help","games","quiz","trivia","ttt","rps","number","guess",
    "hangman","letter","memory","memoryanswer","dice","coin","uno",
    "unojoin","unoleave","unostart","unoplay","unodraw","unocolor",
    "unostatus","wordchain","wcjoin","wcleave","wcstart","wcstatus","wcstop"
]))
async def wc_word_answer(_, m: types.Message):
    k=_wc_key(m); g=_wc_state(k)
    if not g or not g["running"] or not m.text:
        return
    word=m.text.strip().lower()
    if not re.fullmatch(r"[a-z]+",word):
        return
    pid=m.from_user.id
    current_pid=g["players"][g["turn"]][0]
    if pid != current_pid:
        return
    if word not in _WC_WORDS:
        return await m.reply_text("❌ That word isn't in the current Word Chain dictionary.")
    if len(word)<4 or len(word)>6:
        return await m.reply_text("❌ Use a word with 4–6 letters.")
    if word[0] != g["required"]:
        return await m.reply_text(f"❌ Your word must start with **{g['required'].upper()}**.")
    if word in g["used"]:
        return await m.reply_text("❌ That word was already used.")
    # score: one point per letter, matching the spirit of the source game's scoring.
    old=list(g["players"][g["turn"]])
    old[2]+=len(word)
    g["players"][g["turn"]]=tuple(old)
    g["used"].add(word)
    g["last_word"]=word
    g["required"]=word[-1]
    g["turn"]=(g["turn"]+1)%len(g["players"])
    g["deadline"]=asyncio.get_running_loop().time()+40
    if g["turn_task"]:
        g["turn_task"].cancel()
    g["turn_task"]=asyncio.create_task(_wc_timeout(k))
    await m.reply_text(
        f"✅ **{word}** accepted! +{len(word)} points.\n\n{_wc_render(g)}"
    )

@app.on_message(filters.command("games"))
async def wc_games_hint(_, m: types.Message):
    # This is intentionally a separate handler; Telegram will deliver both
    # /games handlers and the main games menu remains available.
    await m.reply_text(
        "🔗 **Word Chain:** `/wordchain` → `/wcjoin` → `/wcstart`\n"
        "During the game, send the next valid word directly."
    )
