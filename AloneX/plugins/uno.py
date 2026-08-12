"""Simple native UNO game for the unified Pyrogram bot."""
import random
from pyrogram import filters, types
from AloneX import app, appdb

COLORS = ["🔴", "🟡", "🟢", "🔵"]
VALUES = ["0","1","2","3","4","5","6","7","8","9","Skip","Reverse","+2"]
GAMES = {}

def deck():
    d=[]
    for c in COLORS:
        d += [(c,v) for v in VALUES]
        d += [(c,v) for v in VALUES if v != "0"]
    d += [("🌈","Wild")]*4 + [("🌈","+4")]*4
    random.shuffle(d)
    return d

def card(c):
    return f"{c[0]} {c[1]}"

@app.on_message(filters.command("uno"))
async def uno_start(_, m: types.Message):
    k=m.chat.id
    if k in GAMES:
        return await m.reply_text("🃏 UNO is already running here.")
    d=deck()
    hands={m.from_user.id:[d.pop() for _ in range(7)]}
    GAMES[k]={"deck":d,"hands":hands,"players":[m.from_user.id],
              "names":{m.from_user.id:m.from_user.first_name or str(m.from_user.id)},
              "turn":0,"discard":d.pop(),"started":False}
    await m.reply_text(
        "🃏 **UNO lobby created!**\n\n"
        "Join with `/unojoin`.\nStart with `/unostart`.\n"
        "This version uses text commands; private card UI can be added later."
    )

@app.on_message(filters.command("unojoin"))
async def uno_join(_, m: types.Message):
    g=GAMES.get(m.chat.id)
    if not g: return await m.reply_text("Start with `/uno`.")
    uid=m.from_user.id
    if uid not in g["players"]:
        if len(g["players"]) >= 8:
            return await m.reply_text("UNO is full.")
        g["players"].append(uid); g["hands"][uid]=[g["deck"].pop() for _ in range(7)]
        g["names"][uid]=m.from_user.first_name or str(uid)
    await m.reply_text(f"✅ {g['names'][uid]} joined. Players: {len(g['players'])}")

@app.on_message(filters.command("unostart"))
async def uno_start_game(_, m: types.Message):
    g=GAMES.get(m.chat.id)
    if not g: return await m.reply_text("Start with `/uno`.")
    if len(g["players"]) < 2: return await m.reply_text("Need at least 2 players.")
    g["started"]=True
    await m.reply_text(
        "🃏 **UNO started!**\n\n"
        f"Top card: **{card(g['discard'])}**\n"
        f"Turn: **{g['names'][g['players'][0]]}**\n"
        "Use `/unohand` to see your cards. (Cards are text for now.)"
    )

@app.on_message(filters.command("unohand"))
async def uno_hand(_, m: types.Message):
    g=GAMES.get(m.chat.id)
    if not g: return await m.reply_text("No UNO game.")
    hand=g["hands"].get(m.from_user.id)
    if hand is None: return await m.reply_text("Join with `/unojoin` first.")
    await m.reply_text("🃏 **Your cards:**\n" + "\n".join(
        f"{i+1}. {card(c)}" for i,c in enumerate(hand)
    ))

@app.on_message(filters.command("unostop"))
async def uno_stop(_, m: types.Message):
    if m.chat.id in GAMES:
        GAMES.pop(m.chat.id,None)
        return await m.reply_text("🛑 UNO stopped.")
    await m.reply_text("No UNO game is running.")
