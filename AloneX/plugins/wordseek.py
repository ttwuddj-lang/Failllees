"""Native WordSeek/Wordle-style game for the unified Pyrogram bot.

This is deliberately a small native implementation: it does not start the
original Node/Bun WordSeek server, so Railway only needs one Telegram bot
process. Scores are persisted through the unified PostgreSQL app database.
"""

import random
import re
from pyrogram import filters, types
from AloneX import app, appdb

_WORDS = sorted(set("""
about above abuse actor acute admit adopt adult after again agent agree ahead alarm album alert alike alive allow alone along alter among anger angle angry apart apple apply arena argue arise array aside asset audio audit avoid awake award aware badly baker basic beach began begin being below bench birth black blame blank blind block blood board brain brand bread break brick bring broad broke brown build built buyer cable carry catch cause chain chair chart chase cheap check chest chief child china chose civil claim class clean clear climb clock close cloud coach coast color count court cover craft crash cream crime cross crowd crown daily dance dealt death debut delay depth devil diary dirty doubt dozen draft drama dream dress drink drive earth eight elite empty enemy enjoy enter entry equal error event every exact exist extra faith false fancy fault favor field fifth fifty fight final first flame flash floor focus force force frame frank fresh front fruit funny giant given glass globe glory grace grade grand grant grass great green group guard guess guest guide happy heart heavy hello house human image index inner input issue ivory judge known label labor large later laugh layer learn least leave legal lemon level light limit local logic loose lucky lunch magic major maker match maybe medal media metal might minor model money month moral motor mouse mouth movie music never night noble noise north novel nurse occur ocean offer often order other outer owner paint panel paper party peace phase phone photo piece pilot place plain plane plant plate point power press price pride prime print prize proof proud quick quiet radio raise range rapid ratio reach ready right river robot rough round route royal ruler rural scale scene scope score sense serve seven shall shape share sharp sheep sheet shift shine shirt shock short sight since skill sleep slice small smart smile smoke solid solve sound south space spare speak speed spend spent sport staff stage stand start state steam steel stick still stone store storm story strip study style sugar suite super table taste teach team thank their theme there these thick thing think third those three throw tiger tight title today topic total touch tower track trade train treat trend trial tribe trick trust truth uncle under union unique unite until upper upset urban usage usual valid value video visit vital voice waste watch water wheel where which while white whole whose woman world worry worth would write wrong young youth zebra
""".split()))
# Ensure a decent fallback pool
if len(_WORDS) < 100:
    _WORDS += ["python","telegram","computer","keyboard","football","rainbow","elephant","mountain"]

_ACTIVE = {}

def _key(m): return (m.chat.id, m.from_user.id)

def _pick():
    return random.choice(_WORDS)

def _mask(word, guesses):
    return " ".join(c if c in guesses else "▫️" for c in word)

@app.on_message(filters.command(["wordseek","ws"]))
async def wordseek_start(_, m: types.Message):
    k=_key(m)
    if k in _ACTIVE:
        g=_ACTIVE[k]
        return await m.reply_text(
            f"🔤 **WordSeek already running**\n\n{_mask(g['word'],g['guesses'])}\n"
            f"Guesses: {g['attempts']}/6\nUse `/ws <word>` to guess."
        )
    word=_pick()
    _ACTIVE[k]={"word":word,"guesses":set(),"attempts":0}
    await appdb.upsert_user(m.from_user.id,m.from_user.username,m.from_user.first_name)
    await m.reply_text(
        "🔤 **WordSeek**\n\n"
        "Guess the hidden 5-letter word.\n"
        "Use `/ws <word>` to submit a guess.\n"
        "You get 6 attempts."
    )

@app.on_message(filters.command(["wshelp"]))
async def wordseek_help(_,m:types.Message):
    await m.reply_text(
        "🔤 **WordSeek commands**\n\n"
        "`/wordseek` — start a game\n"
        "`/ws word` — submit a 5-letter guess\n"
        "`/wshelp` — show help\n"
        "`/wsstats` — show your WordSeek stats"
    )

@app.on_message(filters.command(["wsstats"]))
async def wordseek_stats(_,m:types.Message):
    row=await appdb.get_game_stats(m.from_user.id,"wordseek")
    if not row:
        return await m.reply_text("📊 No WordSeek games played yet.")
    await m.reply_text(
        f"📊 **WordSeek stats**\n\n"
        f"Played: {row['played']}\nWins: {row['wins']}\n"
        f"Losses: {row['losses']}\nScore: {row['score']}"
    )

@app.on_message(filters.command(["ws"]))
async def wordseek_guess(_,m:types.Message):
    k=_key(m)
    g=_ACTIVE.get(k)
    if not g:
        return await m.reply_text("Start first with `/wordseek`.")
    parts=m.text.split(maxsplit=1)
    if len(parts)!=2 or not re.fullmatch(r"[a-zA-Z]{5}",parts[1].strip()):
        return await m.reply_text("Use a **5-letter** guess, e.g. `/ws apple`.")
    guess=parts[1].strip().lower()
    g["attempts"]+=1
    if guess==g["word"]:
        score=max(10,70-(g["attempts"]-1)*10)
        _ACTIVE.pop(k,None)
        await appdb.record_game(m.from_user.id,"wordseek",win=True,score=score)
        return await m.reply_text(
            f"🎉 **Correct!** The word was **{g['word']}**.\n"
            f"Attempts: {g['attempts']}/6\n🏆 +{score} points"
        )
    # Give useful Wordle-like positional feedback.
    feedback=[]
    target=g["word"]
    for i,ch in enumerate(guess):
        if ch==target[i]: feedback.append("🟩")
        elif ch in target: feedback.append("🟨")
        else: feedback.append("⬛")
    if g["attempts"]>=6:
        answer=g["word"]; _ACTIVE.pop(k,None)
        await appdb.record_game(m.from_user.id,"wordseek",loss=True)
        return await m.reply_text(
            f"{' '.join(feedback)}\n\n❌ Game over. Word: **{answer}**"
        )
    await m.reply_text(
        f"{' '.join(feedback)}\n\n"
        f"Attempts: {g['attempts']}/6\n"
        "🟩 correct place • 🟨 wrong place • ⬛ not in word"
    )
