# Mini-games plugin for UnifiedAloneX
# Games: Quiz, Tic-Tac-Toe, RPS, Number Guessing, Hangman,
# Memory, Trivia, Dice and Coin Toss.
#
# All game state is kept in memory. Restarting the bot resets active games.

import random
from pyrogram import filters, types
from AloneX import app

_ttt = {}
_number = {}
_hangman = {}
_memory = {}
_quiz = {}

QUIZ = [
    ("What is the capital of India?", ["Delhi", "Mumbai", "Kolkata", "Chennai"], 0),
    ("Which planet is known as the Red Planet?", ["Earth", "Mars", "Venus", "Jupiter"], 1),
    ("How many continents are there?", ["5", "6", "7", "8"], 2),
    ("Which gas do plants mainly use for photosynthesis?", ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], 2),
    ("Which is the largest ocean?", ["Atlantic", "Indian", "Pacific", "Arctic"], 2),
]

WORDS = ["python", "telegram", "computer", "keyboard", "football", "rainbow", "elephant", "mountain"]

def _key(m):
    return m.chat.id

@app.on_message(filters.command("games"))
async def games(_, m: types.Message):
    await m.reply_text(
        "🎮 **Games available**\n\n"
        "/quiz — Quick quiz\n"
        "/trivia — Trivia question\n"
        "/ttt — Tic-Tac-Toe\n"
        "/rps — Rock Paper Scissors\n"
        "/number — Number guessing\n"
        "/hangman — Hangman\n"
        "/memory — Memory sequence\n"
        "/dice — Roll a die\n"
        "/coin — Flip a coin\n\n"
        "Use `/gamehelp` for examples."
    )

@app.on_message(filters.command("gamehelp"))
async def gamehelp(_, m: types.Message):
    await m.reply_text(
        "🎮 **Game help**\n\n"
        "`/quiz` or `/trivia` — answer with 1, 2, 3 or 4.\n"
        "`/ttt` — send `/ttt 1` to `/ttt 9` to place X.\n"
        "`/rps rock|paper|scissors`\n"
        "`/number` then guess with `/guess 1-100`.\n"
        "`/hangman` then use `/letter a`.\n"
        "`/memory` then repeat the shown sequence with `/memoryanswer 1234`.\n"
        "`/dice` — 1-6; `/coin` — heads/tails."
    )

async def _quiz_start(m):
    q, opts, ans = random.choice(QUIZ)
    _quiz[_key(m)] = ans
    text = "🧠 **Quiz**\n\n" + q + "\n"
    text += "\n".join(f"{i+1}. {x}" for i, x in enumerate(opts))
    await m.reply_text(text)

@app.on_message(filters.command(["quiz", "trivia"]))
async def quiz(_, m):
    await _quiz_start(m)

@app.on_message(filters.command(["answer", "quizanswer"]))
async def quiz_answer(_, m: types.Message):
    if _key(m) not in _quiz:
        return await m.reply_text("Start one with /quiz.")
    try:
        n = int(m.text.split(maxsplit=1)[1])
    except Exception:
        return await m.reply_text("Reply with `/answer 1` to `/answer 4`.")
    correct = _quiz.pop(_key(m))
    await m.reply_text("✅ Correct!" if n - 1 == correct else f"❌ Not quite. Correct answer: {correct+1}.")

def _winner(b):
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b1,c in lines:
        if b[a] and b[a] == b[b1] == b[c]:
            return b[a]
    return "draw" if all(b) else None

def _board(b):
    return "\n".join(
        " | ".join(b[i:i+3]) for i in range(0,9,3)
    ).replace(".", "·")

@app.on_message(filters.command("ttt"))
async def ttt(_, m: types.Message):
    k = _key(m)
    args = m.text.split()
    if len(args) == 1:
        _ttt[k] = ["."] * 9
        return await m.reply_text("❌ Tic-Tac-Toe started. You are X.\nSend `/ttt 1` to `/ttt 9`.\n\n" + _board(_ttt[k]))
    if k not in _ttt:
        return await m.reply_text("Start with /ttt.")
    try:
        p = int(args[1]) - 1
    except Exception:
        return await m.reply_text("Choose a position from 1 to 9.")
    if p not in range(9) or _ttt[k][p] != ".":
        return await m.reply_text("That position isn't available.")
    b = _ttt[k]; b[p] = "X"
    if _winner(b):
        result = _winner(b); _ttt.pop(k, None)
        return await m.reply_text(("🏆 You win!" if result == "X" else "🤝 Draw!") + "\n\n" + _board(b))
    empty = [i for i,x in enumerate(b) if x == "."]
    if empty:
        b[random.choice(empty)] = "O"
    result = _winner(b)
    if result:
        _ttt.pop(k, None)
        return await m.reply_text(("🤖 I win!" if result == "O" else "🤝 Draw!") + "\n\n" + _board(b))
    await m.reply_text("Your turn: `/ttt 1-9`\n\n" + _board(b))

@app.on_message(filters.command("rps"))
async def rps(_, m: types.Message):
    choices = ["rock", "paper", "scissors"]
    try:
        user = m.text.split(maxsplit=1)[1].lower()
    except Exception:
        return await m.reply_text("Use `/rps rock`, `/rps paper` or `/rps scissors`.")
    if user not in choices:
        return await m.reply_text("Choose rock, paper or scissors.")
    bot = random.choice(choices)
    if user == bot: result = "🤝 Draw!"
    elif (user, bot) in [("rock","scissors"),("paper","rock"),("scissors","paper")]: result = "🏆 You win!"
    else: result = "🤖 I win!"
    await m.reply_text(f"✊ You: {user}\n🤖 Bot: {bot}\n\n{result}")

@app.on_message(filters.command("number"))
async def number(_, m: types.Message):
    _number[_key(m)] = random.randint(1,100)
    await m.reply_text("🔢 I'm thinking of a number from 1 to 100.\nUse `/guess 50`.")

@app.on_message(filters.command("guess"))
async def guess(_, m: types.Message):
    k = _key(m)
    if k not in _number:
        return await m.reply_text("Start with /number.")
    try: n = int(m.text.split(maxsplit=1)[1])
    except Exception: return await m.reply_text("Use `/guess 50`.")
    target = _number[k]
    if n == target:
        _number.pop(k); return await m.reply_text("🎯 Correct! You guessed it!")
    await m.reply_text("⬆️ Higher!" if n < target else "⬇️ Lower!")

@app.on_message(filters.command("hangman"))
async def hangman(_, m: types.Message):
    word = random.choice(WORDS)
    _hangman[_key(m)] = {"word": word, "guessed": set(), "tries": 7}
    masked = " ".join("_" for _ in word)
    await m.reply_text(f"🔤 **Hangman**\n\n{masked}\n\nUse `/letter a` to guess a letter. Tries: 7")

@app.on_message(filters.command("letter"))
async def letter(_, m: types.Message):
    k = _key(m)
    if k not in _hangman: return await m.reply_text("Start with /hangman.")
    try: ch = m.text.split(maxsplit=1)[1].lower().strip()[0]
    except Exception: return await m.reply_text("Use `/letter a`.")
    g = _hangman[k]
    if ch in g["guessed"]: return await m.reply_text("You already tried that letter.")
    g["guessed"].add(ch)
    if ch not in g["word"]: g["tries"] -= 1
    shown = " ".join(c if c in g["guessed"] else "_" for c in g["word"])
    if "_" not in shown:
        _hangman.pop(k); return await m.reply_text(f"🎉 You solved it!\n\n{shown}")
    if g["tries"] <= 0:
        word = g["word"]; _hangman.pop(k)
        return await m.reply_text(f"Game over. The word was **{word}**.")
    await m.reply_text(f"{shown}\n\nTries left: {g['tries']}")

@app.on_message(filters.command("memory"))
async def memory(_, m: types.Message):
    seq = "".join(str(random.randint(0,9)) for _ in range(4))
    _memory[_key(m)] = seq
    await m.reply_text(f"🧠 Remember this sequence:\n\n**{seq}**\n\nThen send `/memoryanswer {seq}`.")

@app.on_message(filters.command("memoryanswer"))
async def memory_answer(_, m: types.Message):
    k = _key(m)
    if k not in _memory: return await m.reply_text("Start with /memory.")
    try: ans = m.text.split(maxsplit=1)[1].strip()
    except Exception: return await m.reply_text("Use `/memoryanswer 1234`.")
    seq = _memory.pop(k)
    await m.reply_text("🧠 Excellent memory! ✅" if ans == seq else f"❌ Not correct. The sequence was `{seq}`.")

@app.on_message(filters.command("dice"))
async def dice(_, m: types.Message):
    await m.reply_text(f"🎲 You rolled: **{random.randint(1,6)}**")

@app.on_message(filters.command("coin"))
async def coin(_, m: types.Message):
    await m.reply_text(f"🪙 Coin: **{random.choice(['Heads','Tails'])}**")



async def _uno_send_card_sticker(m, card):
    """Send the local UNO card as a sticker; fallback to text if unavailable."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "uno_stickers", f"{card[0]}-{card[1]}.webp")
    if os.path.exists(path):
        try:
            await m.reply_sticker(path)
            return True
        except Exception:
            pass
    return False


# ---------------- UNO UI ----------------
# Screenshot-style UNO interface:
# - generated game-board image with top card + player's hand
# - inline "Make your choice!" card buttons
# - Draw button
# - 2-4 players
# - commands remain available as fallback

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

_UNO = {}
_UNO_COLORS = ["red", "blue", "green", "yellow"]
_UNO_VALUES = ["0","1","2","3","4","5","6","7","8","9","skip","reverse","draw2"]

def _uno_deck():
    deck = []
    for color in _UNO_COLORS:
        deck.append((color, "0"))
        for value in _UNO_VALUES[1:]:
            deck.extend([(color, value), (color, value)])
    deck += [("wild","wild")] * 4
    deck += [("wild","draw4")] * 4
    random.shuffle(deck)
    return deck

def _uno_card(c):
    return f"{c[0]}-{c[1]}"

def _uno_name(c):
    return {"skip":"SKIP","reverse":"↻","draw2":"+2","draw4":"+4","wild":"WILD"}.get(c[1], c[1].upper())

def _uno_can_play(card, current):
    color, value = card
    cc, cv = current
    return color == "wild" or color == cc or value == cv

def _uno_draw(g, pid, count=1):
    for _ in range(count):
        if not g["deck"]:
            top = g["discard"][-1]
            recycle = g["discard"][:-1]
            random.shuffle(recycle)
            g["deck"] = recycle
            g["discard"] = [top]
        if g["deck"]:
            g["hands"][pid].append(g["deck"].pop())

def _uno_next(g, step=1):
    g["turn"] = (g["turn"] + step) % len(g["players"])

def _uno_font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return None

def _draw_unocard(draw, xy, size, card, scale=1.0):
    x,y=xy
    w,h=size
    palette={"red":(205,42,45),"blue":(42,92,205),"green":(45,160,78),"yellow":(239,184,24),"wild":(55,55,65)}
    c=palette[card[0]]
    draw.rounded_rectangle((x,y,x+w,y+h), radius=int(18*scale), fill=c, outline="white", width=max(2,int(4*scale)))
    draw.ellipse((x+int(w*.10),y+int(h*.16),x+int(w*.90),y+int(h*.84)), fill=(245,245,238))
    label=_uno_name(card)
    font=_uno_font(int(42*scale) if len(label)>2 else int(58*scale))
    if font:
        bb=draw.textbbox((0,0),label,font=font)
        draw.text((x+(w-(bb[2]-bb[0]))/2,y+(h-(bb[3]-bb[1]))/2-8),label,fill=(35,35,35),font=font)

def _uno_board(g, pid):
    # A Telegram-friendly card-board image inspired by the supplied screenshot.
    W,H=1100,760
    img=Image.new("RGB",(W,H),(247,249,240))
    d=ImageDraw.Draw(img)
    title=_uno_font(38)
    sub=_uno_font(25)
    d.text((45,30),"Current game: UNO 🃏",fill=(45,120,65),font=title)
    current=g["current"]
    d.text((45,82),f"Top card: {_uno_card(current)}",fill=(70,70,70),font=sub)
    _draw_unocard(d,(70,140),(210,300),current,1.0)

    pid_turn=g["players"][g["turn"]][0]
    turn_name=g["players"][g["turn"]][1]
    d.text((330,150),f"Turn: {turn_name}",fill=(40,100,160),font=title)
    hand=g["hands"].get(pid,[])
    d.text((330,205),f"Your cards: {len(hand)}",fill=(70,70,70),font=sub)

    # Show up to 8 cards in the image, with remaining count.
    shown=hand[:8]
    card_w,card_h=115,165
    start_x=300
    gap=8
    for i,card in enumerate(shown):
        _draw_unocard(d,(start_x+i*(card_w+gap),260),(card_w,card_h),card,.65)
    if len(hand)>8:
        d.text((start_x+8*(card_w+gap),320),f"+{len(hand)-8}",fill=(30,30,30),font=title)

    footer=_uno_font(28)
    d.text((45,690),"Make your choice with the buttons below 👇",fill=(55,120,70),font=footer)
    bio=BytesIO()
    img.save(bio,"PNG")
    bio.seek(0)
    return bio

def _uno_keyboard(g, pid):
    buttons=[]
    hand=g["hands"].get(pid,[])
    current=g["current"]
    for i,card in enumerate(hand):
        if _uno_can_play(card,current):
            label={"skip":"⛔","reverse":"🔄","draw2":"+2","draw4":"+4","wild":"🌈"}.get(card[1],card[1])
            buttons.append(InlineKeyboardButton(
                f"{label} {card[0]}", callback_data=f"uno:play:{i}"
            ))
    rows=[]
    for i in range(0,len(buttons),3):
        rows.append(buttons[i:i+3])
    rows.append([InlineKeyboardButton("📥 Draw", callback_data="uno:draw")])
    rows.append([InlineKeyboardButton("🃏 My Cards", callback_data="uno:hand")])
    return InlineKeyboardMarkup(rows)

async def _uno_render(client, chat_id, g, pid, message=None):
    bio=_uno_board(g,pid)
    kb=_uno_keyboard(g,pid)
    if message:
        try:
            await message.edit_media(
                types.InputMediaPhoto(bio, caption="🃏 **UNO** — Make your choice!")
            )
            await message.edit_reply_markup(kb)
            return
        except Exception:
            pass
    await client.send_photo(
        chat_id,
        bio,
        caption="🃏 **UNO** — Make your choice!",
        reply_markup=kb
    )

async def _uno_end(client, chat_id, g, winner_name):
    g["finished"]=True
    await client.send_message(chat_id, f"🏆 **{winner_name} wins UNO!**")

@app.on_message(filters.command("uno"))
async def uno(_, m: types.Message):
    k=_key(m)
    if k in _UNO and not _UNO[k]["finished"]:
        return await m.reply_text("🃏 An UNO game already exists here. Use /unojoin or /unostatus.")
    _UNO[k]={
        "players":[(m.from_user.id,m.from_user.first_name or "Player")],
        "hands":{}, "deck":[], "discard":[], "turn":0, "current":None,
        "finished":False, "started":False
    }
    await m.reply_text("🃏 **Created a new UNO game!**\n\nJoin with `/unojoin` and start with `/unostart`.")

@app.on_message(filters.command("unojoin"))
async def uno_join(_, m: types.Message):
    k=_key(m)
    if k not in _UNO: return await m.reply_text("Start with /uno.")
    g=_UNO[k]
    if g["started"]: return await m.reply_text("The game has already started.")
    pid=m.from_user.id
    if any(p[0]==pid for p in g["players"]): return await m.reply_text("You already joined.")
    if len(g["players"])>=4: return await m.reply_text("Lobby is full (4 players).")
    g["players"].append((pid,m.from_user.first_name or "Player"))
    await m.reply_text(f"Joined the game — {len(g['players'])}/4 players.")

@app.on_message(filters.command("unostart"))
async def uno_start(client, m: types.Message):
    k=_key(m)
    if k not in _UNO: return await m.reply_text("Start with /uno.")
    g=_UNO[k]
    if g["started"]: return await m.reply_text("Game already started.")
    if len(g["players"])<2: return await m.reply_text("Need at least 2 players.")
    g["started"]=True
    g["deck"]=_uno_deck()
    g["hands"]={pid:[] for pid,_ in g["players"]}
    for _ in range(7):
        for pid,_ in g["players"]: _uno_draw(g,pid)
    while True:
        c=g["deck"].pop()
        if c[0]!="wild":
            g["discard"]=[c]; g["current"]=c; break
        g["deck"].insert(0,c); random.shuffle(g["deck"])
    g["turn"]=0
    pid,name=g["players"][0]
    await m.reply_text(f"🎮 **UNO started!**\nFirst player: **{name}**")
    await _uno_render(client,m.chat.id,g,pid)

@app.on_callback_query(filters.regex(r"^uno:"))
async def uno_callback(client, q: CallbackQuery):
    k=q.message.chat.id
    if k not in _UNO or _UNO[k]["finished"]:
        return await q.answer("No active UNO game.",show_alert=True)
    g=_UNO[k]
    pid=q.from_user.id
    if not any(p[0]==pid for p in g["players"]):
        return await q.answer("Join the game first.",show_alert=True)
    if not g["started"]:
        return await q.answer("Game hasn't started.",show_alert=True)
    if g["players"][g["turn"]][0]!=pid:
        return await q.answer("It's not your turn.",show_alert=True)
    action=q.data.split(":")[1]
    if action=="hand":
        hand=g["hands"].get(pid,[])
        return await q.answer("Your hand: "+", ".join(_uno_card(c) for c in hand),show_alert=True)
    if action=="draw":
        _uno_draw(g,pid)
        drawn=g["hands"][pid][-1]
        await q.answer(f"Drew {_uno_card(drawn)}")
        if _uno_can_play(drawn,g["current"]):
            await _uno_render(client,k,g,pid,q.message)
        else:
            _uno_next(g)
            await _uno_render(client,k,g,g["players"][g["turn"]][0],q.message)
        return
    if action=="play":
        try: idx=int(q.data.split(":")[2])
        except: return await q.answer("Invalid card.",show_alert=True)
        hand=g["hands"][pid]
        if idx<0 or idx>=len(hand): return await q.answer("Card no longer exists.",show_alert=True)
        card=hand[idx]
        if not _uno_can_play(card,g["current"]):
            return await q.answer("You can't play that card.",show_alert=True)
        hand.pop(idx); g["discard"].append(card); g["current"]=card
        if not hand:
            await q.answer("UNO! 🎉")
            name=next(n for p,n in g["players"] if p==pid)
            await _uno_end(client,k,g,name)
            return
        if card[0]=="wild":
            # Ask the player to choose a color with four inline buttons.
            kb=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔴 Red",callback_data="uno:color:red"),
                InlineKeyboardButton("🔵 Blue",callback_data="uno:color:blue"),
            ],[
                InlineKeyboardButton("🟢 Green",callback_data="uno:color:green"),
                InlineKeyboardButton("🟡 Yellow",callback_data="uno:color:yellow"),
            ]])
            await q.answer("Choose a color.")
            await q.message.reply_text("🌈 **Choose the new color:**",reply_markup=kb)
            return
        if card[1]=="skip":
            _uno_next(g,2)
        elif card[1]=="reverse":
            if len(g["players"])>2:
                g["players"].reverse()
            _uno_next(g)
        elif card[1]=="draw2":
            _uno_next(g)
            _uno_draw(g,g["players"][g["turn"]][0],2)
        else:
            _uno_next(g)
        await q.answer(f"Played {_uno_card(card)}")
        await _uno_render(client,k,g,g["players"][g["turn"]][0],q.message)
        return
    if action=="color":
        color=q.data.split(":")[2]
        if color not in _UNO_COLORS: return await q.answer("Invalid color.",show_alert=True)
        g["current"]=(color,g["current"][1])
        _uno_next(g)
        await q.answer(f"Color: {color}")
        await _uno_render(client,k,g,g["players"][g["turn"]][0],q.message)

@app.on_message(filters.command("unostatus"))
async def uno_status(_,m:types.Message):
    k=_key(m)
    if k not in _UNO: return await m.reply_text("No UNO game here.")
    g=_UNO[k]
    if not g["started"]:
        return await m.reply_text(f"🃏 UNO lobby: {len(g['players'])}/4")
    name=g["players"][g["turn"]][1]
    await m.reply_text(f"🃏 Top card: **{_uno_card(g['current'])}**\n➡️ Turn: **{name}**")

@app.on_message(filters.command("unoleave"))
async def uno_leave(_,m:types.Message):
    k=_key(m)
    if k not in _UNO: return await m.reply_text("No UNO game here.")
    g=_UNO[k]
    if g["started"]: return await m.reply_text("You can't leave after the game starts.")
    pid=m.from_user.id
    g["players"]=[p for p in g["players"] if p[0]!=pid]
    await m.reply_text("You left the UNO lobby.")

