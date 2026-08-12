import random
import os
import json
import html
import asyncio
import time
from datetime import datetime, timezone

from groq import Groq

from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env variable missing")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
ACTIVE_FILE = "active_members.json"
GAME_BAN_FILE = "connect_game_banned.json"
CONNECT_LB_FILE = "connect_leaderboard.json"
ECONOMY_FILE = "economy.json"

START_PHOTO = "https://kommodo.ai/i/IOLcEhfHnTNODGFnUBQI"
HELP_PHOTO = START_PHOTO
FORCE_CHANNEL = "@JP_NETWORK"
SUPPORT_LINK = "https://t.me/jp_network"

JOIN_TIME = 30
MAX_LEVELS = 10

COUPLE_PHOTOS = [
    "https://kommodo.ai/i/zxgdh45YyX2vk9HaNBlE",
    "https://kommodo.ai/i/bBggBx9cyGNz2iEBkaSg"
]

GIFS = {
    "slap": "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "kiss": "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
    "hug": "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
    "pat": "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
    "bite": "https://media.giphy.com/media/1Bgr0VaRnx3pCZbaJa/giphy.gif",
    "punch": "https://media.giphy.com/media/l1J3G5lf06vi58EIE/giphy.gif",
    "kill": "https://media.giphy.com/media/3ohhwfAa9rbXaZe86c/giphy.gif",
    "dance": "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "cry": "https://media.giphy.com/media/OPU6wzx8JrHna/giphy.gif"
}



BASE_OPPOSITE_PAIRS = [('good', 'bad'), ('hot', 'cold'), ('big', 'small'), ('up', 'down'), ('open', 'closed'), ('day', 'night'), ('rich', 'poor'), ('fast', 'slow'), ('new', 'old'), ('yes', 'no'), ('true', 'false'), ('high', 'low'), ('near', 'far'), ('left', 'right'), ('in', 'out'), ('top', 'bottom'), ('full', 'empty'), ('wet', 'dry'), ('hard', 'soft'), ('clean', 'dirty'), ('long', 'short'), ('light', 'dark'), ('weak', 'strong'), ('black', 'white'), ('sweet', 'bitter'), ('happy', 'sad'), ('brave', 'fearful'), ('kind', 'cruel'), ('safe', 'dangerous'), ('loud', 'quiet'), ('fresh', 'stale'), ('real', 'fake'), ('same', 'different'), ('alive', 'dead'), ('awake', 'asleep'), ('start', 'end'), ('come', 'go'), ('front', 'back'), ('early', 'late'), ('easy', 'difficult'), ('right', 'wrong'), ('calm', 'angry'), ('sharp', 'blunt'), ('cheap', 'expensive'), ('rare', 'common'), ('clear', 'cloudy'), ('polite', 'rude'), ('pure', 'impure'), ('known', 'unknown'), ('upper', 'lower'), ('inner', 'outer'), ('fair', 'unfair'), ('lucky', 'unlucky'), ('useful', 'useless'), ('first', 'last'), ('past', 'future'), ('north', 'south'), ('east', 'west'), ('single', 'double'), ('even', 'odd'), ('raw', 'cooked'), ('host', 'guest'), ('win', 'lose'), ('buy', 'sell'), ('give', 'take'), ('send', 'receive'), ('sit', 'stand'), ('push', 'pull'), ('hide', 'show'), ('add', 'remove'), ('ask', 'answer'), ('break', 'fix'), ('cry', 'laugh'), ('fail', 'pass'), ('love', 'hate'), ('lock', 'unlock'), ('rise', 'fall'), ('float', 'sink'), ('trust', 'doubt'), ('save', 'spend'), ('more', 'less'), ('all', 'none'), ('many', 'few'), ('on', 'off'), ('male', 'female'), ('boy', 'girl'), ('man', 'woman'), ('king', 'queen'), ('sun', 'moon'), ('life', 'death'), ('truth', 'lie'), ('peace', 'war'), ('smile', 'frown'), ('entry', 'exit'), ('enable', 'disable'), ('create', 'delete'), ('join', 'leave'), ('mix', 'split'), ('grow', 'shrink'), ('permit', 'forbid'), ('always', 'never'), ('profit', 'loss'), ('credit', 'debit'), ('import', 'export'), ('online', 'offline'), ('login', 'logout'), ('major', 'minor'), ('plus', 'minus'), ('smart', 'dumb'), ('wise', 'foolish'), ('proud', 'humble'), ('loose', 'tight'), ('hungry', 'full'), ('tall', 'short'), ('fat', 'thin'), ('messy', 'clean'), ('rough', 'smooth'), ('warm', 'cool'), ('free', 'busy'), ('noisy', 'silent'), ('solid', 'liquid'), ('city', 'village'), ('land', 'water'), ('heaven', 'hell'), ('spring', 'autumn'), ('summer', 'winter'), ('morning', 'evening'), ('inside', 'outside'), ('above', 'below'), ('accept', 'reject'), ('allow', 'deny'), ('attack', 'defend'), ('borrow', 'lend'), ('catch', 'throw'), ('enter', 'exit'), ('forget', 'remember'), ('raise', 'lower'), ('teach', 'learn'), ('tie', 'untie'), ('visible', 'hidden'), ('victory', 'defeat'), ('friend', 'enemy'), ('hero', 'villain'), ('leader', 'follower'), ('parent', 'child'), ('doctor', 'patient'), ('driver', 'passenger'), ('owner', 'tenant'), ('admin', 'member'), ('public', 'private'), ('secret', 'open'), ('manual', 'automatic'), ('analog', 'digital'), ('original', 'copy'), ('empty', 'filled'), ('normal', 'strange'), ('quick', 'slow'), ('bright', 'dim'), ('thin', 'thick'), ('wide', 'narrow'), ('deep', 'shallow'), ('tiny', 'huge'), ('floor', 'roof'), ('question', 'answer'), ('input', 'output'), ('seller', 'buyer'), ('gold', 'silver'), ('maximum', 'minimum'), ('best', 'worst'), ('better', 'worse'), ('young', 'old'), ('forward', 'backward'), ('clockwise', 'anticlockwise'), ('arrival', 'departure'), ('advance', 'retreat'), ('adult', 'child'), ('after', 'before'), ('against', 'for'), ('agree', 'disagree'), ('appear', 'vanish'), ('approve', 'disapprove'), ('ascent', 'descent'), ('attract', 'repel'), ('beautiful', 'ugly'), ('begin', 'finish'), ('bend', 'straighten'), ('bless', 'curse'), ('bold', 'timid'), ('build', 'destroy'), ('careful', 'careless'), ('certain', 'uncertain'), ('combine', 'separate'), ('comfort', 'pain'), ('complex', 'simple'), ('conceal', 'reveal'), ('connect', 'disconnect'), ('constant', 'variable'), ('construct', 'demolish'), ('contract', 'expand'), ('courage', 'fear'), ('cover', 'uncover'), ('defend', 'attack'), ('deposit', 'withdraw'), ('despair', 'hope'), ('divide', 'unite'), ('domestic', 'wild'), ('encourage', 'discourage'), ('equal', 'unequal'), ('external', 'internal'), ('famous', 'unknown'), ('firm', 'weak'), ('fold', 'unfold'), ('foreign', 'native'), ('formal', 'casual'), ('found', 'lost'), ('freedom', 'slavery'), ('freeze', 'melt'), ('gain', 'lose'), ('generous', 'selfish'), ('gentle', 'rough'), ('guilty', 'innocent'), ('harmful', 'helpful'), ('healthy', 'sick'), ('heavy', 'light'), ('honest', 'dishonest'), ('horizontal', 'vertical'), ('include', 'exclude'), ('increase', 'decrease'), ('inhale', 'exhale'), ('intentional', 'accidental'), ('interesting', 'boring'), ('junior', 'senior'), ('legal', 'illegal'), ('loyal', 'disloyal'), ('mature', 'immature'), ('modern', 'ancient'), ('natural', 'artificial'), ('obedient', 'disobedient'), ('optional', 'required'), ('ordinary', 'special'), ('permanent', 'temporary'), ('positive', 'negative'), ('possible', 'impossible'), ('regular', 'irregular'), ('repair', 'damage'), ('reward', 'punish'), ('scatter', 'gather'), ('severe', 'mild'), ('sour', 'sweet'), ('straight', 'curved'), ('strict', 'lenient'), ('success', 'failure'), ('support', 'oppose'), ('tame', 'wild'), ('transparent', 'opaque'), ('urban', 'rural'), ('valuable', 'worthless'), ('virtue', 'vice'), ('wealth', 'poverty'), ('welcome', 'farewell'), ('whisper', 'shout'), ('winner', 'loser'), ('work', 'rest'), ('zenith', 'nadir'), ('active', 'passive'), ('admit', 'deny'), ('aid', 'hinder'), ('alert', 'sleepy'), ('ancestor', 'descendant'), ('angel', 'devil'), ('arrogant', 'modest'), ('ascending', 'descending'), ('balanced', 'unbalanced'), ('belief', 'doubt'), ('birth', 'death'), ('boil', 'freeze'), ('capture', 'release'), ('center', 'edge'), ('chaos', 'order'), ('cheerful', 'gloomy'), ('clumsy', 'graceful'), ('comedy', 'tragedy'), ('competent', 'incompetent'), ('confess', 'deny'), ('confident', 'shy'), ('conquer', 'surrender'), ('conscious', 'unconscious'), ('consent', 'refuse'), ('continue', 'stop'), ('correct', 'incorrect'), ('danger', 'safety'), ('dawn', 'dusk'), ('definite', 'vague'), ('delight', 'sorrow'), ('demand', 'supply'), ('dense', 'sparse'), ('depart', 'arrive'), ('dirty', 'spotless'), ('disease', 'health'), ('drunk', 'sober'), ('dull', 'bright'), ('dwarf', 'giant'), ('eager', 'reluctant'), ('educated', 'ignorant'), ('efficient', 'wasteful'), ('elastic', 'rigid'), ('employer', 'employee'), ('evil', 'good'), ('exact', 'approximate'), ('expensive', 'cheap'), ('fact', 'fiction'), ('fade', 'brighten'), ('familiar', 'strange'), ('fancy', 'plain'), ('fasten', 'loosen'), ('feeble', 'strong'), ('fertile', 'barren'), ('final', 'initial'), ('find', 'lose'), ('flat', 'steep'), ('flexible', 'stiff'), ('frugal', 'wasteful'), ('general', 'specific'), ('genuine', 'fake'), ('glad', 'sorry'), ('gradual', 'sudden'), ('harmony', 'discord'), ('harsh', 'gentle'), ('heal', 'injure'), ('help', 'hurt'), ('hollow', 'solid'), ('honor', 'shame'), ('idle', 'busy'), ('ignorance', 'knowledge'), ('ill', 'well'), ('imperfect', 'perfect'), ('indoor', 'outdoor'), ('inferior', 'superior'), ('inflate', 'deflate'), ('insane', 'sane'), ('insult', 'praise'), ('intelligent', 'stupid'), ('joy', 'sorrow'), ('landlord', 'tenant'), ('large', 'little'), ('lazy', 'active'), ('lead', 'follow'), ('lengthen', 'shorten'), ('liberty', 'captivity'), ('likely', 'unlikely'), ('limited', 'limitless'), ('living', 'dead'), ('logical', 'illogical'), ('majority', 'minority'), ('married', 'single'), ('mercy', 'cruelty'), ('misery', 'joy'), ('motion', 'rest'), ('noble', 'mean'), ('noon', 'midnight'), ('offense', 'defense'), ('optimist', 'pessimist'), ('orderly', 'messy'), ('outgoing', 'incoming'), ('part', 'whole'), ('patient', 'impatient'), ('perfect', 'flawed'), ('perish', 'survive'), ('plenty', 'scarcity'), ('powerful', 'weak'), ('praise', 'criticize'), ('presence', 'absence'), ('pretty', 'ugly'), ('proceed', 'halt'), ('protect', 'harm'), ('rarely', 'often'), ('refined', 'crude'), ('reluctant', 'eager'), ('remote', 'near'), ('repulsive', 'attractive'), ('restless', 'calm'), ('rigid', 'flexible'), ('sane', 'insane'), ('scarce', 'plentiful'), ('secretive', 'open'), ('seldom', 'often'), ('shameful', 'honorable'), ('similar', 'opposite'), ('simplify', 'complicate'), ('sin', 'virtue'), ('slim', 'fat'), ('sober', 'drunk'), ('special', 'ordinary'), ('stable', 'unstable'), ('subtract', 'add'), ('sufficient', 'lacking'), ('sunset', 'sunrise'), ('superficial', 'deep'), ('suspect', 'trust'), ('tender', 'tough'), ('thankful', 'thankless'), ('timely', 'late'), ('total', 'partial'), ('unique', 'common'), ('vacant', 'occupied'), ('visitor', 'host'), ('voluntary', 'forced'), ('waste', 'save'), ('wealthy', 'poor'), ('willing', 'unwilling'), ('scarcity', 'abundance'), ('abundance', 'shortage'), ('accurate', 'inaccurate'), ('adaptable', 'rigid'), ('addicted', 'free'), ('advanced', 'basic'), ('affirm', 'negate'), ('aggressive', 'peaceful'), ('agreeable', 'disagreeable'), ('alive', 'lifeless'), ('ancient', 'recent'), ('approval', 'refusal'), ('arise', 'settle'), ('arrival', 'leaving'), ('assemble', 'disassemble'), ('attachment', 'detachment'), ('attentive', 'careless'), ('authentic', 'counterfeit'), ('available', 'missing'), ('awkward', 'graceful'), ('bare', 'covered'), ('barren', 'fertile'), ('benefit', 'harm'), ('beneath', 'above'), ('bestow', 'withhold'), ('broad', 'narrow'), ('busy', 'idle'), ('capable', 'incapable'), ('care', 'neglect'), ('cautious', 'reckless'), ('central', 'remote'), ('charming', 'repulsive'), ('civil', 'rude'), ('civilized', 'savage'), ('coarse', 'fine'), ('coldness', 'warmth'), ('collect', 'scatter'), ('commonplace', 'rare'), ('complete', 'incomplete'), ('compulsory', 'optional'), ('concave', 'convex'), ('confirm', 'deny'), ('confusion', 'clarity'), ('conserve', 'waste'), ('content', 'discontent'), ('courteous', 'impolite'), ('cowardly', 'brave'), ('creation', 'destruction'), ('crooked', 'straight'), ('crowded', 'empty'), ('crude', 'refined'), ('daytime', 'nighttime'), ('decent', 'indecent'), ('decline', 'improve'), ('delay', 'hurry'), ('delicate', 'tough'), ('dependent', 'independent'), ('different', 'same'), ('disclose', 'conceal'), ('distantly', 'closely'), ('diverse', 'same'), ('doubtful', 'sure'), ('downstairs', 'upstairs'), ('drag', 'push'), ('dreary', 'cheerful'), ('earn', 'spend'), ('ebb', 'flow'), ('effect', 'cause'), ('elevate', 'lower'), ('enemy', 'ally'), ('enlarge', 'reduce'), ('enough', 'insufficient'), ('erase', 'write'), ('exactly', 'roughly'), ('expose', 'hide'), ('extreme', 'moderate'), ('failure', 'success'), ('faithful', 'faithless'), ('farther', 'nearer'), ('fearless', 'fearful'), ('feminine', 'masculine'), ('fill', 'empty'), ('fixed', 'loose'), ('flatter', 'insult'), ('follow', 'lead'), ('forgive', 'blame'), ('fragile', 'strong'), ('frank', 'secretive'), ('gathering', 'scattering'), ('grateful', 'ungrateful'), ('growth', 'decline'), ('harden', 'soften'), ('hasty', 'slow'), ('hopeful', 'hopeless'), ('hostile', 'friendly'), ('imaginary', 'real'), ('independent', 'dependent'), ('indirect', 'direct'), ('insecure', 'secure'), ('intended', 'accidental'), ('joyful', 'sad'), ('kindly', 'unkind'), ('lawful', 'unlawful'), ('lengthy', 'brief'), ('liberal', 'strict'), ('lighten', 'darken'), ('little', 'large'), ('lively', 'dull'), ('loosen', 'tighten'), ('loving', 'hateful'), ('malice', 'kindness'), ('masculine', 'feminine'), ('meaningful', 'meaningless'), ('meek', 'proud'), ('merry', 'sad'), ('misty', 'clear'), ('moving', 'still'), ('native', 'foreign'), ('neat', 'messy'), ('necessary', 'needless'), ('obedient', 'rebellious'), ('openly', 'secretly'), ('optimism', 'pessimism'), ('outward', 'inward'), ('over', 'under'), ('partial', 'total'), ('plain', 'fancy'), ('pleasant', 'unpleasant'), ('polished', 'rough'), ('precise', 'vague'), ('pulling', 'pushing'), ('purely', 'impurely'), ('quickly', 'slowly'), ('reduce', 'increase'), ('release', 'capture'), ('resist', 'surrender'), ('rural', 'urban'), ('shout', 'whisper'), ('shut', 'open'), ('sleep', 'wake'), ('soften', 'harden'), ('some', 'none'), ('speedy', 'slow'), ('stingy', 'generous'), ('succeed', 'fail'), ('sunny', 'rainy'), ('survive', 'perish'), ('talk', 'listen'), ('together', 'apart'), ('trouble', 'peace'), ('unfair', 'fair'), ('unite', 'divide'), ('unseen', 'seen'), ('upstairs', 'downstairs'), ('usual', 'unusual'), ('vertical', 'horizontal'), ('wasteful', 'frugal'), ('within', 'outside'), ('youngest', 'oldest'), ('zero', 'infinite')]

def build_opposite_pairs():
    pairs = []
    seen = set()

    def add_pair(a, b):
        a = str(a).lower().strip()
        b = str(b).lower().strip()
        if not a or not b or a == b:
            return
        if (a, b) not in seen:
            pairs.append((a, b))
            seen.add((a, b))
        if (b, a) not in seen:
            pairs.append((b, a))
            seen.add((b, a))

    for a, b in BASE_OPPOSITE_PAIRS:
        add_pair(a, b)

    # Extra generated variants only for opposite game variety
    prefixes = [
        "very", "super", "ultra", "mega", "mini", "micro", "macro", "neo", "anti",
        "pre", "post", "sub", "over", "under", "inner", "outer", "upper", "lower",
        "main", "side", "first", "last", "early", "late", "daily", "nightly",
        "hyper", "semi", "multi", "mono", "auto", "manual", "home", "away",
        "red", "blue", "green", "dark", "light", "gold", "silver", "royal"
    ]
    roots = [
        ("good","bad"),("hot","cold"),("open","closed"),("up","down"),("left","right"),
        ("happy","sad"),("light","dark"),("win","lose"),("start","finish"),("enter","exit"),
        ("push","pull"),("give","take"),("buy","sell"),("true","false"),("high","low"),
        ("full","empty"),("rich","poor"),("near","far"),("fast","slow"),("clean","dirty"),
        ("safe","dangerous"),("loud","quiet"),("fresh","stale"),("alive","dead"),("young","old"),
        ("big","small"),("hard","soft"),("wet","dry"),("kind","cruel"),("brave","fearful")
    ]

    for p in prefixes:
        for a, b in roots:
            add_pair(p + a, p + b)
            if len(pairs) >= 1300:
                return pairs[:1300]

    return pairs

OPPOSITE_PAIRS = build_opposite_pairs()

def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

users = load_data(USERS_FILE, [])
groups = load_data(GROUPS_FILE, [])
active_members = load_data(ACTIVE_FILE, {})
game_banned = load_data(GAME_BAN_FILE, {})
connect_leaderboard = load_data(CONNECT_LB_FILE, {})
economy_data = load_data(ECONOMY_FILE, {})
chatbot_status = {}
connect_games = {}

def get_name(user):
    return user.first_name or "User"

def mention_user(user):
    return f'<a href="tg://user?id={user.id}">{html.escape(user.first_name or "User")}</a>'

def mention_member(member):
    return f'<a href="tg://user?id={member["id"]}">{html.escape(member["name"])}</a>'

def track_active(update: Update):
    if not update.effective_user or not update.effective_chat:
        return
    chat = update.effective_chat
    user = update.effective_user
    if user.id not in users:
        users.append(user.id)
        save_data(USERS_FILE, users)
    if chat.type not in ["group", "supergroup"]:
        return
    if chat.id not in groups:
        groups.append(chat.id)
        save_data(GROUPS_FILE, groups)
    cid = str(chat.id)
    active_members.setdefault(cid, [])
    active_members[cid] = [m for m in active_members[cid] if m["id"] != user.id]
    active_members[cid].append({"id": user.id, "name": get_name(user)})
    save_data(ACTIVE_FILE, active_members)

def get_random_member(chat_id, exclude_id=None):
    members = active_members.get(str(chat_id), [])
    if exclude_id:
        members = [m for m in members if m["id"] != exclude_id]
    return random.choice(members) if members else None

async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        return True
    if update.effective_chat.type not in ["group", "supergroup"]:
        return False
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(FORCE_CHANNEL, update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# =========================
# ECONOMY SYSTEM
# =========================

START_BALANCE = 270
REVIVE_COST = 500
PROTECT_COST_PER_DAY = 500
ROB_TAX_RATE = 0.10
GIVE_TAX_RATE = 0.10
DAILY_BET_LIMIT = 200
BET_SPAM_BLOCK_SECONDS = 600

def save_economy():
    save_data(ECONOMY_FILE, economy_data)

def now_ts():
    return int(time.time())

def today_key():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def eco_user(uid, name="User"):
    uid = str(uid)
    if uid not in economy_data:
        economy_data[uid] = {
            "name": name,
            "balance": START_BALANCE,
            "xp": 0,
            "kills": 0,
            "alive": False,
            "last_daily": "",
            "shield_until": 0,
            "bets_today": 0,
            "bet_day": today_key(),
            "bet_streak": 0,
            "best_bet_streak": 0,
            "last_bet_ts": 0,
            "bet_spam_count": 0,
            "bet_block_until": 0
        }
    economy_data[uid]["name"] = name
    economy_data[uid].setdefault("balance", START_BALANCE)
    economy_data[uid].setdefault("xp", 0)
    economy_data[uid].setdefault("kills", 0)
    economy_data[uid].setdefault("alive", False)
    economy_data[uid].setdefault("last_daily", "")
    economy_data[uid].setdefault("shield_until", 0)
    economy_data[uid].setdefault("bets_today", 0)
    economy_data[uid].setdefault("bet_day", today_key())
    economy_data[uid].setdefault("bet_streak", 0)
    economy_data[uid].setdefault("best_bet_streak", 0)
    economy_data[uid].setdefault("last_bet_ts", 0)
    economy_data[uid].setdefault("bet_spam_count", 0)
    economy_data[uid].setdefault("bet_block_until", 0)
    return economy_data[uid]

def fmt_money(amount):
    try:
        amount = float(amount)
    except:
        amount = 0
    if amount.is_integer():
        return f"{int(amount):,}"
    return f"{amount:,.2f}"

def parse_amount(text):
    if not text:
        return None
    text = str(text).lower().replace(",", "").replace("$", "").strip()
    try:
        if "+" in text:
            a, b = text.split("+", 1)
            return int(float(a) * (10 ** int(float(b))))
        return int(float(text))
    except:
        return None

def eco_balance_rank(uid):
    users_sorted = sorted(
        economy_data.items(),
        key=lambda x: float(x[1].get("balance", 0)),
        reverse=True
    )
    uid = str(uid)
    for i, (user_id, _) in enumerate(users_sorted, 1):
        if user_id == uid:
            return i
    return len(users_sorted) + 1

def eco_xp_rank(uid):
    users_sorted = sorted(
        economy_data.items(),
        key=lambda x: int(x[1].get("xp", 0)),
        reverse=True
    )
    uid = str(uid)
    for i, (user_id, _) in enumerate(users_sorted, 1):
        if user_id == uid:
            return i
    return len(users_sorted) + 1

def is_protected(user_data):
    return int(user_data.get("shield_until", 0)) > now_ts()

def shield_left(user_data):
    left = int(user_data.get("shield_until", 0)) - now_ts()
    if left <= 0:
        return ""
    days = left // 86400
    hours = (left % 86400) // 3600
    mins = (left % 3600) // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"

def eco_mention_from_id(uid, name):
    return f'<a href="tg://user?id={uid}">{html.escape(name or "User")}</a>'

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    user = update.effective_user
    data = eco_user(user.id, get_name(user))
    save_economy()
    status = "Alive" if data.get("alive") else "Dead"
    text = (
        f"👤 Name: {mention_user(user)}\n"
        f"💰 Balance: ${fmt_money(data.get('balance', 0))}\n"
        f"🏆 Rank: {eco_balance_rank(user.id)}\n"
        f"⚔️ Kills: {data.get('kills', 0)}\n"
        f"💜 Status: {status}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    if update.effective_chat.type != "private":
        await update.message.reply_text("Daily rewards can only be claimed in DMs.")
        return

    user = update.effective_user
    data = eco_user(user.id, get_name(user))

    if data.get("last_daily") == today_key():
        await update.message.reply_text("⏳ Aaj ka daily reward already claim ho chuka hai.\nCome back tomorrow for more!")
        return

    cash = random.randint(500, 1500)
    xp = max(10, int(cash / 50))
    data["balance"] = float(data.get("balance", 0)) + cash
    data["xp"] = int(data.get("xp", 0)) + xp
    data["alive"] = True
    data["last_daily"] = today_key()
    save_economy()

    await update.message.reply_text(
        f"🎁 Daily reward:\n"
        f"💰 ${fmt_money(cash)}\n"
        f"⭐️ {xp}XP\n\n"
        f"Come back tomorrow for more!"
    )

async def give_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    if not update.message.reply_to_message:
        await update.message.reply_text("Pay who? Please specify a user.")
        return

    amount = parse_amount(context.args[0]) if context.args else None
    if not amount or amount <= 0:
        await update.message.reply_text("Usage: /give <amount> reply karke")
        return

    sender = update.effective_user
    target = update.message.reply_to_message.from_user
    if target.id == sender.id:
        await update.message.reply_text("❌ Khud ko money nahi de sakte.")
        return

    sdata = eco_user(sender.id, get_name(sender))
    tdata = eco_user(target.id, get_name(target))
    tax = amount * GIVE_TAX_RATE
    receive = amount - tax

    if sdata.get("balance", 0) < amount:
        await update.message.reply_text("❌ Balance kam hai.")
        return

    sdata["balance"] -= amount
    tdata["balance"] += receive
    sdata["xp"] += 1
    tdata["alive"] = True
    save_economy()

    await update.message.reply_text(
        f"Transaction successful!\n\n"
        f"💰 Sent: ${fmt_money(receive)}\n"
        f"💸 Tax deducted: ${fmt_money(tax)}\n"
        f"👤 {mention_user(sender)} ➜ {mention_user(target)}",
        parse_mode=ParseMode.HTML
    )

async def toprich_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(economy_data.items(), key=lambda x: float(x[1].get("balance", 0)), reverse=True)[:10]
    if not top:
        await update.message.reply_text("❌ Leaderboard empty hai.")
        return
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 <b>Global leaderboard</b> 🏆\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, (uid, data) in enumerate(top, 1):
        prefix = medals[i-1] if i <= 3 else f"{i}."
        text += f"{prefix} {eco_mention_from_id(uid, data.get('name', 'User'))} ➣ ${fmt_money(data.get('balance',0))} Coins\n"
    text += "━━━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def rank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    eco_user(user.id, get_name(user))
    save_economy()
    await update.message.reply_text(
        f"{mention_user(user)}'S rank is #{eco_xp_rank(user.id)}.",
        parse_mode=ParseMode.HTML
    )

async def rob_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    if not update.message.reply_to_message:
        await update.message.reply_text("Rob who? Please specify a user.")
        return
    amount = parse_amount(context.args[0]) if context.args else None
    if not amount or amount <= 0:
        amount = random.randint(100, 320)

    robber = update.effective_user
    target = update.message.reply_to_message.from_user
    if target.id == robber.id:
        await update.message.reply_text("❌ Khud ko rob nahi kar sakte.")
        return

    rdata = eco_user(robber.id, get_name(robber))
    tdata = eco_user(target.id, get_name(target))

    if is_protected(tdata):
        await update.message.reply_text("🛡 Target protected hai. Rob failed.")
        return
    if tdata.get("balance", 0) < amount:
        await update.message.reply_text("❌ Target ke pass itna balance nahi hai.")
        return

    success = random.random() < 0.50
    if not success:
        penalty = min(amount, rdata.get("balance", 0))
        rdata["balance"] -= penalty
        save_economy()
        await update.message.reply_text(f"❌ Rob failed!\nYou lost ${fmt_money(penalty)}.")
        return

    tax = amount * ROB_TAX_RATE
    gain = amount - tax
    tdata["balance"] -= amount
    rdata["balance"] += gain
    rdata["xp"] += 3
    save_economy()

    await update.message.reply_text(
        f"🔪 Rob successful!\n\n"
        f"{mention_user(target)} just got financially deleted for ${fmt_money(amount)} 💀\n\n"
        f"Tax deducted: ${fmt_money(tax)}",
        parse_mode=ParseMode.HTML
    )

async def kill_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    if not update.message.reply_to_message:
        await update.message.reply_text("Kill who? Please specify a user.")
        return
    amount = parse_amount(context.args[0]) if context.args else None
    if not amount or amount <= 0:
        amount = random.randint(100, 320)

    killer = update.effective_user
    target = update.message.reply_to_message.from_user
    if target.id == killer.id:
        await update.message.reply_text("❌ Khud ko kill nahi kar sakte.")
        return

    kdata = eco_user(killer.id, get_name(killer))
    tdata = eco_user(target.id, get_name(target))

    if is_protected(tdata):
        await update.message.reply_text("🛡 Target protected hai. Kill failed.")
        return
    if kdata.get("balance", 0) < amount:
        await update.message.reply_text("❌ Balance kam hai.")
        return

    success = random.random() < 0.55
    kdata["balance"] -= amount

    if success:
        reward = int(amount * 0.70)
        kdata["balance"] += reward
        kdata["kills"] = int(kdata.get("kills", 0)) + 1
        kdata["xp"] += 10
        tdata["alive"] = False
        save_economy()
        await update.message.reply_text(
            f"{mention_user(killer)} just deleted {mention_user(target)} from existence 💀 (+${fmt_money(reward)})",
            parse_mode=ParseMode.HTML
        )
    else:
        save_economy()
        await update.message.reply_text(f"❌ Kill failed! Bounty ${fmt_money(amount)} lost.")

async def protect_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    if not context.args:
        await update.message.reply_text(
            "Invalid time format.\n\nUse 1d for 1 day protection\nuse 2d for 2 days protection\n\nExample: /protect 1D"
        )
        return

    arg = context.args[0].lower()
    if arg not in ["1d", "2d"]:
        await update.message.reply_text(
            "Invalid time format.\n\nUse 1d for 1 day protection\nuse 2d for 2 days protection\n\nExample: /protect 1D"
        )
        return

    days = int(arg[0])
    cost = PROTECT_COST_PER_DAY * days
    user = update.effective_user
    data = eco_user(user.id, get_name(user))

    if data.get("balance", 0) < cost:
        await update.message.reply_text(f"❌ Protection cost ${fmt_money(cost)} hai. Balance kam hai.")
        return

    data["balance"] -= cost
    data["shield_until"] = now_ts() + days * 86400
    save_economy()
    await update.message.reply_text(f"🛡 Protection activated for {days} day(s)!\nCost: ${fmt_money(cost)}")

async def shield_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = eco_user(user.id, get_name(user))
    if not is_protected(data):
        await update.message.reply_text("You are not currently protected from attacks.")
        return
    await update.message.reply_text(f"🛡 You are protected.\nTime left: {shield_left(data)}")

async def revive_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    if not update.message.reply_to_message:
        await update.message.reply_text("Revive who? Please reply to a dead user.")
        return

    reviver = update.effective_user
    target = update.message.reply_to_message.from_user
    rdata = eco_user(reviver.id, get_name(reviver))
    tdata = eco_user(target.id, get_name(target))

    if rdata.get("balance", 0) < REVIVE_COST:
        await update.message.reply_text(f"❌ Revive cost ${REVIVE_COST}. Balance kam hai.")
        return
    if tdata.get("alive"):
        await update.message.reply_text("✅ User already alive hai.")
        return

    rdata["balance"] -= REVIVE_COST
    tdata["alive"] = True
    save_economy()
    await update.message.reply_text(
        f"{mention_user(target)} Has been revived By {mention_user(reviver)} For ${REVIVE_COST}.",
        parse_mode=ParseMode.HTML
    )

async def topkill_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(economy_data.items(), key=lambda x: int(x[1].get("kills", 0)), reverse=True)[:10]
    top = [(uid, data) for uid, data in top if int(data.get("kills", 0)) > 0]
    if not top:
        await update.message.reply_text("❌ Kills leaderboard empty hai.")
        return
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 <b>Kills leaderboard</b> 🏆\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, (uid, data) in enumerate(top, 1):
        prefix = medals[i-1] if i <= 3 else f"{i}."
        text += f"{prefix} {eco_mention_from_id(uid, data.get('name','User'))} ➣ {data.get('kills',0)} Kills\n"
    text += "━━━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def bet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, raw_amount=None):
    track_active(update)
    user = update.effective_user
    data = eco_user(user.id, get_name(user))
    day = today_key()

    if data.get("bet_day") != day:
        data["bet_day"] = day
        data["bets_today"] = 0
        data["bet_spam_count"] = 0

    if now_ts() < int(data.get("bet_block_until", 0)):
        left = int(data.get("bet_block_until", 0)) - now_ts()
        await update.message.reply_text(f"🚫 Bet spam block active hai. Wait {left//60} min.")
        return

    if data.get("bets_today", 0) >= DAILY_BET_LIMIT:
        await update.message.reply_text("⚠️ Daily limit reached: 200 bets.")
        return

    current = now_ts()
    if current - int(data.get("last_bet_ts", 0)) < 2:
        data["bet_spam_count"] = int(data.get("bet_spam_count", 0)) + 1
        if data["bet_spam_count"] >= 5:
            data["bet_block_until"] = current + BET_SPAM_BLOCK_SECONDS
            save_economy()
            await update.message.reply_text("🚫 Spamming detected. 10 min block.")
            return
    else:
        data["bet_spam_count"] = 0

    data["last_bet_ts"] = current

    if raw_amount is None:
        raw_amount = context.args[0] if context.args else None
    amount = parse_amount(raw_amount)

    if not amount or amount <= 0:
        await update.message.reply_text("Usage: /bet <amount>\nExample: /bet 100\nbbet 5+3 = $5000")
        return

    if data.get("balance", 0) < amount:
        await update.message.reply_text("❌ Balance kam hai.")
        return

    data["bets_today"] += 1
    win = random.random() < 0.50

    if win:
        data["balance"] += amount
        data["xp"] += max(1, int(amount / 100))
        data["bet_streak"] = int(data.get("bet_streak", 0)) + 1
        data["best_bet_streak"] = max(int(data.get("best_bet_streak", 0)), data["bet_streak"])
        save_economy()
        await update.message.reply_text(
            f"🎰 Bet Won!\n\n"
            f"💰 Bet: ${fmt_money(amount)}\n"
            f"✅ Profit: ${fmt_money(amount)}\n"
            f"🔥 Streak: {data['bet_streak']}"
        )
    else:
        data["balance"] -= amount
        data["bet_streak"] = 0
        save_economy()
        await update.message.reply_text(
            f"🎰 Bet Lost!\n\n"
            f"💸 Lost: ${fmt_money(amount)}\n"
            f"🍀 Better luck next time!"
        )

async def bbet_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text.lower().startswith("bbet "):
        return False
    raw = text.split(maxsplit=1)[1].strip()
    await bet_cmd(update, context, raw_amount=raw)
    return True

async def games_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🎮 <b>Games Commands</b> 🎮

🔗 <b>Opposite Chain Game</b>
/startconnectwin
/join
/startchaingame
/chaingamehelp
/endconnectwin
/cleaderboard

💰 <b>Economy</b>
/balance /bal
/daily
/give &lt;amount&gt;
/toprich /leaderboard
/rank

🎰 <b>Betting</b>
/bet &lt;amount&gt;
bbet &lt;amount&gt;
bbet 1+1
bbet 5+3

🔪 <b>Actions</b>
/rob &lt;amount&gt; optional
/kill &lt;amount&gt; optional
/protect 1d
/shield /protection
/revive
/topkill"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ!", url=SUPPORT_LINK),
            InlineKeyboardButton("ᴏᴡɴᴇʀ!", url=f"tg://user?id={OWNER_ID}")
        ],
        [InlineKeyboardButton("✅ ᴠᴇʀɪꜰʏ", callback_data="verify_join")]
    ])
    caption = """💕 Hieeeeee

ɪ'ᴍ ᴀᴅᴀ ✨
ɪ ʜᴀᴠᴇ ᴀ ʟᴏᴛ ᴏꜰ ꜰᴇᴀᴛᴜʀᴇꜱ ɪɴ ᴛʜɪꜱ ʙᴏᴛ ꜱᴏ
ᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ꜰᴇᴀᴛᴜʀᴇꜱ ....!

ꜰɪʀꜱᴛ ᴊᴏɪɴ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴠᴇʀɪꜰʏ ✅"""
    await update.message.reply_photo(photo=START_PHOTO, caption=caption, reply_markup=keyboard)

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_joined(update, context):
        await query.message.reply_text("✅ ᴠᴇʀɪꜰɪᴇᴅ!\n\nɴᴏᴡ ᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ꜰᴇᴀᴛᴜʀᴇꜱ ✨")
    else:
        await query.message.reply_text("❌ ᴘᴇʜʟᴇ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ ᴊᴏɪɴ ᴋᴀʀᴏ.\n\n@jp_network")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot"), InlineKeyboardButton("ꜰᴜɴ", callback_data="help_fun")],
        [InlineKeyboardButton("ʀᴇᴘʟʏ ꜰᴜɴ", callback_data="help_replyfun"), InlineKeyboardButton("🎮 ɢᴀᴍᴇꜱ", callback_data="help_games")],
        [InlineKeyboardButton("💰 ᴇᴄᴏɴᴏᴍʏ", callback_data="help_economy"), InlineKeyboardButton("🔪 ᴀᴄᴛɪᴏɴ", callback_data="help_action")],
        [InlineKeyboardButton("ɢʀᴏᴜᴘ ʜᴇʟᴘ", callback_data="help_group"), InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ!", url=SUPPORT_LINK)]
    ])
    caption = """Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ. Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.

Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /"""
    await update.message.reply_photo(photo=HELP_PHOTO, caption=caption, reply_markup=keyboard)

async def help_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = {
        "help_chatbot": """🤖 ᴄʜᴀᴛʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs

/start
/help
/chatbot on
/chatbot off
/stats
/broadcast message
/tagall message""",
        "help_fun": """💕 ꜰᴜɴ ᴄᴏᴍᴍᴀɴᴅs

/couples
/crush
/brain
/love""",
        "help_replyfun": """🎭 ʀᴇᴘʟʏ ꜰᴜɴ ᴄᴏᴍᴍᴀɴᴅs

/slap
/kiss
/hug
/pat
/bite
/punch
/kill
/dance
/cry

Kisi user ke message ko reply karke command use karo.""",
        "help_game": """🔗 ᴏᴘᴘᴏꜱɪᴛᴇ ᴄʜᴀɪɴ ɢᴀᴍᴇ

/startconnectwin
/join
/startchaingame
/chaingamehelp
/endconnectwin
/cleaderboard
/Baningame reply
/Unbaningame reply

Queue turn system
Correct +1 | Miss -1
3 miss = Run out
Hint button current player ke liye""",
        "help_games": """🎮 ɢᴀᴍᴇꜱ

/startconnectwin
/join
/startchaingame
/chaingamehelp
/endconnectwin
/cleaderboard

/balance /bal
/daily
/give <amount>
/toprich /leaderboard
/rank

/bet <amount>
bbet <amount>

/rob <amount>
/kill <amount>
/protect
/shield
/revive
/topkill""",

        "help_economy": """💰 ᴇᴄᴏɴᴏᴍʏ ᴄᴏᴍᴍᴀɴᴅs

/balance Or /bal - Check balance and XP
/daily - Claim daily cash reward in DM
/give <amount> - Reply and transfer money
/toprich Or /leaderboard - Richest players
/rank - Global XP rank

🎰 Bet:
/bet <amount>
bbet <amount>
bbet 1+1
bbet 5+3""",

        "help_action": """🔪 ᴀᴄᴛɪᴏɴ ᴄᴏᴍᴍᴀɴᴅs

/rob <amount> - Reply rob, amount optional
/kill <amount> - Reply kill, amount optional
/protect 1d - Buy shield
/shield Or /protection - Check shield
/revive - Reply and revive dead user
/topkill - Top assassins""",

        "help_group": """🛡 ɢʀᴏᴜᴘ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs

/ban reply
/unban reply
/mute reply
/unmute reply

Bot ko admin banana zaroori hai."""
    }
    await query.message.reply_text(texts.get(query.data, "❌ No help found."))

async def chaingamehelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🔗 ᴏᴘᴘᴏꜱɪᴛᴇ ᴄʜᴀɪɴ ɢᴀᴍᴇ ʜᴇʟᴘ

/startconnectwin - game room banao
/join - game me join karo
/startchaingame - admin/owner game start
/endconnectwin - admin/owner game end
/cleaderboard - group leaderboard

🎮 ɢᴀᴍᴇ ᴋᴀɪꜱᴇ ᴋʜᴇʟɴᴀ ʜᴀɪ?

1. /startconnectwin bhejo.
2. Players /join bhej kar game me aayenge.
3. Minimum 2 players chahiye.
4. Room creator ya koi joined player /startchaingame dega.
5. Bot line/queue me turn dega: A ➜ B ➜ C ➜ A
6. Jiska turn hai sirf wahi answer dega.
7. Bot word dega aur opposite puchhega.

Example:
Word: Gold
Hint: Si _ _ _ _

Answer:
silver

8. Correct answer = +1 point.
9. Time over = -1 point aur bot correct answer dikha dega.
10. 3 miss hone ke baad player run out.
11. Time 30 sec se start hoga, har round 2 sec kam hoga, minimum 10 sec.
12. Har player ek baar 💡 Use Hint button use kar sakta hai.

⚠️ Note:
Hint button sirf current turn wale player ke liye chalega."""
    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(f"👥 Users: {len(users)}\n📢 Groups: {len(groups)}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("Usage: /broadcast message")
        return
    sent_users = sent_groups = 0
    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            sent_users += 1
        except:
            pass
    for gid in groups:
        try:
            await context.bot.send_message(gid, msg)
            sent_groups += 1
        except:
            pass
    await update.message.reply_text(f"✅ Broadcast Sent\nUsers: {sent_users}\nGroups: {sent_groups}")

async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ /chatbot on/off sirf group me use karo.")
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/chatbot on\n/chatbot off")
        return

    chat_id = update.effective_chat.id
    mode = context.args[0].lower()

    if mode == "on":
        chatbot_status[chat_id] = True
        await update.message.reply_text("✅ Chatbot ON\nAb is group me AI chatting aur sticker reply dono ON rahenge.")

    elif mode == "off":
        chatbot_status[chat_id] = False
        await update.message.reply_text("❌ Chatbot OFF\nAb is group me AI chatting aur sticker reply dono band rahenge. Sirf game chalega.")

    else:
        await update.message.reply_text("Usage:\n/chatbot on\n/chatbot off")


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        mention = f'<a href="tg://user?id={member.id}">{html.escape(member.first_name or "User")}</a>'
        if member.id == context.bot.id:
            await update.message.reply_text("💕 ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ!\n\nᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ꜰᴇᴀᴛᴜʀᴇꜱ ✨")
        else:
            await update.message.reply_text(
                f"""🎉 Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Gʀᴏᴜᴘ 🎉

{mention}

🆔 ID: <code>{member.id}</code>

Hᴀᴠᴇ Fᴜɴ Aɴᴅ Eɴᴊᴏʏ ✨""",
                parse_mode=ParseMode.HTML
            )

async def tagall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command sirf group me chalega.")
        return
    if not await is_admin_or_owner(update, context):
        await update.message.reply_text("❌ Sirf admin /tagall use kar sakta hai.")
        return
    msg = " ".join(context.args) or "Attention everyone!"
    members = active_members.get(str(chat.id), [])
    if not members:
        await update.message.reply_text("❌ Active members nahi mile.")
        return
    text = f"🦋 {html.escape(msg)}\n\n"
    for i, m in enumerate(members, 1):
        text += mention_member(m) + " "
        if i % 5 == 0:
            text += "\n"
        if len(text) > 3500:
            await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)
            text = ""
    if text:
        await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)

async def couples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat_id = update.effective_chat.id
    members = active_members.get(str(chat_id), [])
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command group me use karo.")
        return
    if len(members) < 2:
        await update.message.reply_text("❌ Active members kam hai. Group me thoda chat karo.")
        return
    user1, user2 = random.sample(members, 2)
    caption = f"""❤️ TODAY'S CUTE COUPLE ❤️

{mention_member(user1)} 🔥 💞 {mention_member(user2)}

LOVE IS IN THE AIR ❤️

~ FROM ADA WITH LOVE 💋"""
    try:
        await context.bot.send_photo(chat_id, random.choice(COUPLE_PHOTOS), caption=caption, parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)

async def crush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    user = update.effective_user
    crush_user = get_random_member(update.effective_chat.id, exclude_id=user.id)
    if not crush_user:
        await update.message.reply_text("❌ Active members kam hai.")
        return
    percent = random.randint(1, 100)
    await update.message.reply_text(
        f"💘 {mention_user(user)}'s Sᴇᴄʀᴇᴛ Cʀᴜꜱʜ Iꜱ - {mention_member(crush_user)}\n\nCrush level: {percent}% ❤️",
        parse_mode=ParseMode.HTML
    )

async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    iq = random.randint(1, 100)
    await update.message.reply_text(f"🧠 IQ Lᴇᴠᴇʟ Oꜰ {mention_user(update.effective_user)} Iꜱ {iq}% 😎", parse_mode=ParseMode.HTML)

async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    members = active_members.get(str(update.effective_chat.id), [])
    if len(members) < 2:
        await update.message.reply_text("❌ Active members kam hai.")
        return
    user1, user2 = random.sample(members, 2)
    percent = random.randint(1, 100)
    await update.message.reply_text(
        f"""❤️ Lᴏᴠᴇ Mᴇᴛᴇʀ Rᴇᴘᴏʀᴛ ❤️

{mention_member(user1)} ❤️ {mention_member(user2)}

Lᴏᴠᴇ Cᴏᴍᴘᴀᴛɪʙɪʟɪᴛʏ: {percent}% ❤️""",
        parse_mode=ParseMode.HTML
    )

async def action_command(update: Update, context: ContextTypes.DEFAULT_TYPE, action):
    track_active(update)
    if not update.message.reply_to_message:
        await update.message.reply_text(f"Kisi ke message ko reply karke /{action} do.")
        return
    sender = mention_user(update.effective_user)
    target = mention_user(update.message.reply_to_message.from_user)
    text_map = {
        "slap": f"{sender} slapped {target} 👋",
        "kiss": f"{sender} kissed {target} 😘",
        "hug": f"{sender} hugged {target} 🤗",
        "pat": f"{sender} patted {target} 🥰",
        "bite": f"{sender} bit {target} 😈",
        "punch": f"{sender} punched {target} 👊",
        "kill": f"{sender} killed {target} ☠️",
        "dance": f"{sender} danced with {target} 💃",
        "cry": f"{sender} is crying for {target} 😭"
    }
    caption = text_map[action]
    try:
        await context.bot.send_animation(update.effective_chat.id, GIFS[action], caption=caption, parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)

async def slap(update, context): await action_command(update, context, "slap")
async def kiss(update, context): await action_command(update, context, "kiss")
async def hug(update, context): await action_command(update, context, "hug")
async def pat(update, context): await action_command(update, context, "pat")
async def bite(update, context): await action_command(update, context, "bite")
async def punch(update, context): await action_command(update, context, "punch")
async def kill(update, context): await action_command(update, context, "kill")
async def dance(update, context): await action_command(update, context, "dance")
async def cry(update, context): await action_command(update, context, "cry")

def is_game_banned(chat_id, user_id):
    return str(user_id) in game_banned.get(str(chat_id), [])

def add_game_ban(chat_id, user_id):
    cid, uid = str(chat_id), str(user_id)
    game_banned.setdefault(cid, [])
    if uid not in game_banned[cid]:
        game_banned[cid].append(uid)
    save_data(GAME_BAN_FILE, game_banned)

def remove_game_ban(chat_id, user_id):
    cid, uid = str(chat_id), str(user_id)
    if cid in game_banned and uid in game_banned[cid]:
        game_banned[cid].remove(uid)
    save_data(GAME_BAN_FILE, game_banned)

def add_connect_point(chat_id, user, points=1):
    cid, uid = str(chat_id), str(user.id)
    connect_leaderboard.setdefault(cid, {})
    connect_leaderboard[cid].setdefault(uid, {"name": get_name(user), "points": 0, "wins": 0})
    connect_leaderboard[cid][uid]["name"] = get_name(user)
    connect_leaderboard[cid][uid]["points"] += points
    connect_leaderboard[cid][uid]["wins"] += 1
    save_data(CONNECT_LB_FILE, connect_leaderboard)

def make_blank_word(word):
    word = word.lower()
    if len(word) <= 3:
        return word[0] + "_" * (len(word) - 1)
    return word[:2] + "_" * (len(word) - 2)

def format_chain(chain):
    visible = chain[:-1]
    answer = chain[-1]
    blank = make_blank_word(answer)
    return " 🔗 ".join([w.title() for w in visible]) + f" 🔗 <b>{blank.title()}</b>"

async def connectwin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat, user = update.effective_chat, update.effective_user

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ ConnectWin sirf group me chalega.")
        return

    if is_game_banned(chat.id, user.id):
        await update.message.reply_text("❌ Tum ConnectWin game se banned ho.")
        return

    if chat.id in connect_games:
        await update.message.reply_text(
            "⚠️ Game room already bana hua hai.\n"
            "Players /join kare, phir admin/owner /startchaingame de."
        )
        return

    connect_games[chat.id] = {
        "joining": True,
        "active": False,
        "creator_id": user.id,
        "players": {},          # user_id: name
        "player_order": [],     # fixed turn order
        "turn_index": 0,
        "score": {},
        "misses": {},           # user_id: miss count
        "hints_used": {},       # user_id: bool
        "current_player": None,
        "current_word": None,
        "current_answer": None,
        "round": 0,
        "time_limit": 30,
        "answered": False,
        "used_words": [],
        "round_task": None
    }

    await update.message.reply_text(
        "🔗 ᴏᴘᴘᴏꜱɪᴛᴇ ᴄʜᴀɪɴ ɢᴀᴍᴇ ʀᴏᴏᴍ ᴄʀᴇᴀᴛᴇᴅ!\n\n"
        "Khelne ke liye /join bhejo.\n"
        "Minimum players: 2\n\n"
        "Room creator ya joined player game start karne ke liye /startchaingame de."
    )


async def startchaingame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command sirf group me chalega.")
        return

    game = connect_games.get(chat.id)

    if not game:
        await update.message.reply_text("❌ Abhi game room nahi bana. Pehle /startconnectwin do.")
        return

    allowed_start = (
        await is_admin_or_owner(update, context)
        or update.effective_user.id == game.get("creator_id")
        or update.effective_user.id in game.get("players", {})
    )

    if not allowed_start:
        await update.message.reply_text("❌ Game start karne ke liye pehle /join karo.")
        return

    if game.get("active"):
        await update.message.reply_text("⚠️ Game already started hai.")
        return

    if len(game["players"]) < 2:
        await update.message.reply_text("❌ Minimum 2 players chahiye. Players ko /join karne bolo.")
        return

    # Random order sirf start me banega, phir line/queue me turn chalega
    game["player_order"] = list(game["players"].keys())
    random.shuffle(game["player_order"])
    game["turn_index"] = 0
    game["joining"] = False
    game["active"] = True

    order_text = " ➜ ".join([html.escape(game["players"][uid]) for uid in game["player_order"]])

    await update.message.reply_text(
        f"✅ Game started!\nPlayers: {len(game['players'])}\n\n"
        f"Turn line:\n{order_text}\n\n"
        "Rule: Jiska turn aayega wahi opposite word likhega.\n"
        "Correct = +1 point | Miss = -1 point\n"
        "3 miss hone ke baad player run out.\n"
        "Time 30 sec se start hoga, har round 2 sec kam hoga, minimum 10 sec.\n"
        "Har player 1 baar 💡 hint use kar sakta hai."
    )

    await send_next_opposite_round(chat.id, context)


async def join_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat, user = update.effective_chat, update.effective_user

    if chat.type not in ["group", "supergroup"]:
        return

    if is_game_banned(chat.id, user.id):
        await update.message.reply_text("❌ Tum ConnectWin game se banned ho.")
        return

    game = connect_games.get(chat.id)

    if not game or not game.get("joining"):
        await update.message.reply_text("❌ Abhi koi join session nahi chal raha.")
        return

    if user.id in game["players"]:
        await update.message.reply_text("⚠️ Tum already joined ho.")
        return

    game["players"][user.id] = get_name(user)
    game["score"].setdefault(user.id, 0)
    game["misses"].setdefault(user.id, 0)
    game["hints_used"].setdefault(user.id, False)

    await update.message.reply_text(
        f"✅ {mention_user(user)} joined game!\nAb koi bhi joined player /startchaingame de sakta hai.",
        parse_mode=ParseMode.HTML
    )


def make_answer_hint(answer):
    answer = answer.lower().strip()
    if len(answer) <= 2:
        return answer.title()
    return answer[:2].title() + " " + " ".join(["_"] * (len(answer) - 2))


def get_next_player_id(game):
    order = game.get("player_order", [])
    if not order:
        return None

    # turn_index se next active player lo
    for _ in range(len(order)):
        idx = game["turn_index"] % len(order)
        uid = order[idx]
        game["turn_index"] = (idx + 1) % len(order)

        if uid in game["players"]:
            return uid

    return None


def remove_player_from_order(game, player_id):
    if player_id in game.get("player_order", []):
        game["player_order"] = [uid for uid in game["player_order"] if uid != player_id]
        if game["player_order"]:
            game["turn_index"] %= len(game["player_order"])
        else:
            game["turn_index"] = 0


async def send_next_opposite_round(chat_id, context: ContextTypes.DEFAULT_TYPE):
    game = connect_games.get(chat_id)
    if not game or not game.get("active"):
        return

    if len(game["players"]) <= 1:
        await finish_opposite_game(chat_id, context)
        return

    game["round"] += 1
    game["time_limit"] = max(10, 30 - ((game["round"] - 1) * 2))
    game["answered"] = False

    player_id = get_next_player_id(game)
    if not player_id:
        await finish_opposite_game(chat_id, context)
        return

    game["current_player"] = player_id

    available = [p for p in OPPOSITE_PAIRS if p[0] not in game["used_words"]]
    if not available:
        game["used_words"] = []
        available = OPPOSITE_PAIRS[:]

    word, answer = random.choice(available)
    game["current_word"] = word.lower()
    game["current_answer"] = answer.lower()
    game["used_words"].append(word)

    try:
        member = await context.bot.get_chat_member(chat_id, player_id)
        mention = mention_user(member.user)
    except:
        mention = html.escape(game["players"].get(player_id, "Player"))

    hint_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("💡 Use Hint (1/1)", callback_data=f"opphint:{player_id}")]
    ])

    msg = await context.bot.send_message(
        chat_id,
        f"🎯 Turn: {mention}\n"
        f"⏰ Time: <b>{game['time_limit']} sec</b>\n"
        f"❌ Miss: <b>{game['misses'].get(player_id, 0)}/3</b>\n\n"
        f"Word: <b>{html.escape(word.title())}</b>\n"
        f"Hint: <b>{html.escape(make_answer_hint(answer))}</b>\n\n"
        f"Iska opposite English me likho!",
        parse_mode=ParseMode.HTML,
        reply_markup=hint_button
    )

    game["turn_message_id"] = msg.message_id

    task = context.application.create_task(round_timeout(chat_id, player_id, game["round"], context))
    game["round_task"] = task


async def round_timeout(chat_id, player_id, round_no, context: ContextTypes.DEFAULT_TYPE):
    game = connect_games.get(chat_id)
    if not game:
        return

    await asyncio.sleep(game.get("time_limit", 30))

    game = connect_games.get(chat_id)
    if not game or not game.get("active"):
        return

    if game.get("round") != round_no:
        return

    if game.get("answered"):
        return

    name = game["players"].get(player_id, "Player")
    answer = game.get("current_answer", "")
    word = game.get("current_word", "")

    game["score"][player_id] = game["score"].get(player_id, 0) - 1
    game["misses"][player_id] = game["misses"].get(player_id, 0) + 1
    misses = game["misses"][player_id]

    if misses >= 3:
        game["players"].pop(player_id, None)
        remove_player_from_order(game, player_id)
        await context.bot.send_message(
            chat_id,
            f"⏰ Time over!\n\n"
            f"Word: <b>{html.escape(word.title())}</b>\n"
            f"Correct Answer: <b>{html.escape(answer.title())}</b>\n\n"
            f"❌ <b>{html.escape(name)}</b> -1 Point\n"
            f"💀 3 miss ho gaya, run out!",
            parse_mode=ParseMode.HTML
        )
    else:
        await context.bot.send_message(
            chat_id,
            f"⏰ Time over!\n\n"
            f"Word: <b>{html.escape(word.title())}</b>\n"
            f"Correct Answer: <b>{html.escape(answer.title())}</b>\n\n"
            f"❌ <b>{html.escape(name)}</b> -1 Point\n"
            f"Miss: <b>{misses}/3</b>\n"
            f"Turn next player ko ja raha hai.",
            parse_mode=ParseMode.HTML
        )

    if len(game["players"]) <= 1:
        await finish_opposite_game(chat_id, context)
    else:
        await send_next_opposite_round(chat_id, context)


async def hint_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if not data.startswith("opphint:"):
        return

    try:
        target_id = int(data.split(":", 2)[1])
    except:
        return

    chat_id = query.message.chat.id
    user = query.from_user
    game = connect_games.get(chat_id)

    if not game or not game.get("active"):
        await query.answer("Game active nahi hai.", show_alert=True)
        return

    if user.id != target_id or user.id != game.get("current_player"):
        await query.answer("❌ Ye hint tumhare liye nahi hai.", show_alert=True)
        return

    if game["hints_used"].get(user.id):
        await query.answer("❌ Tum apna hint pehle hi use kar chuke ho.", show_alert=True)
        return

    game["hints_used"][user.id] = True
    answer = game.get("current_answer", "")
    word = game.get("current_word", "")

    try:
        mention = mention_user(user)
        used_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💡 Hint Used (0/1)", callback_data=f"opphint:{user.id}:used")]
        ])

        await query.message.edit_text(
            f"🎯 Turn: {mention}\n"
            f"⏰ Time: <b>{game['time_limit']} sec</b>\n"
            f"❌ Miss: <b>{game['misses'].get(user.id, 0)}/3</b>\n\n"
            f"Word: <b>{html.escape(word.title())}</b>\n"
            f"💡 Hint Used!\n"
            f"Answer: <b>{html.escape(answer.title())}</b>\n\n"
            f"Ab opposite word chat me likho!",
            parse_mode=ParseMode.HTML,
            reply_markup=used_keyboard
        )
    except:
        await query.message.reply_text(
            f"💡 Hint Used!\nAnswer: <b>{html.escape(answer.title())}</b>",
            parse_mode=ParseMode.HTML
        )


async def finish_opposite_game(chat_id, context: ContextTypes.DEFAULT_TYPE):
    game = connect_games.get(chat_id)
    if not game:
        return

    scores = game.get("score", {})
    winner_id = None

    # Agar last player bacha hai to usko winner bonus
    if game.get("players"):
        winner_id = list(game["players"].keys())[0]
        scores[winner_id] = scores.get(winner_id, 0) + 10
    elif scores:
        winner_id = max(scores, key=scores.get)

    if winner_id:
        try:
            member = await context.bot.get_chat_member(chat_id, winner_id)
            winner_name = get_name(member.user)
            add_connect_point(chat_id, member.user, scores.get(winner_id, 0))
        except:
            winner_name = game.get("players", {}).get(winner_id, "Winner")
    else:
        winner_name = "No Winner"

    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 <b>Opposite Chain Game Finished</b>\n\n"
    text += f"🥇 Winner: <b>{html.escape(str(winner_name))}</b>\n"
    text += "🎁 Winner Bonus: +10\n\n"
    text += "📊 Final Scores:\n"

    for uid, score in top:
        name = game["players"].get(uid, f"Player {uid}")
        text += f"• {html.escape(str(name))} - {score}\n"

    connect_games.pop(chat_id, None)
    await context.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)


async def endconnectwin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command sirf group me chalega.")
        return

    if not await is_admin_or_owner(update, context):
        await update.message.reply_text("❌ Sirf owner/admin game end kar sakta hai.")
        return

    if chat.id not in connect_games:
        await update.message.reply_text("❌ Abhi koi game nahi chal raha.")
        return

    game = connect_games.pop(chat.id, None)
    task = game.get("round_task") if game else None
    if task:
        task.cancel()

    await update.message.reply_text("✅ Game end kar diya gaya.")


async def send_love_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id,
            reaction=[{"type": "emoji", "emoji": "❤️"}],
            is_big=False
        )
    except Exception:
        pass


async def connect_guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, user = update.effective_chat, update.effective_user

    if not chat or chat.type not in ["group", "supergroup"]:
        return False

    game = connect_games.get(chat.id)

    if not game or not game.get("active"):
        return False

    # Sirf jis player ka turn hai wahi answer de sakta hai
    if user.id != game.get("current_player"):
        return False

    if is_game_banned(chat.id, user.id):
        return True

    guess = (update.message.text or "").strip().lower()
    answer = game.get("current_answer")

    if guess == answer:
        await send_love_reaction(update, context)
        game["answered"] = True
        game["score"][user.id] = game["score"].get(user.id, 0) + 1

        task = game.get("round_task")
        if task:
            task.cancel()

        await update.message.reply_text(
            f"✅ Correct {mention_user(user)}!\n"
            f"{html.escape(game['current_word'].title())} ➜ <b>{html.escape(answer.title())}</b>\n"
            f"+1 Point",
            parse_mode=ParseMode.HTML
        )

        await asyncio.sleep(1)
        await send_next_opposite_round(chat.id, context)
        return True

    # Current player ne wrong answer diya, isko AI chat me mat bhejo
    return True
async def cleaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    cid = str(chat.id)
    data = connect_leaderboard.get(cid, {})
    if not data:
        await update.message.reply_text("❌ Abhi is group me leaderboard empty hai.")
        return
    top = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:10]
    text = "🏆 <b>ConnectWin Group Leaderboard</b>\n\n"
    for i, (_, info) in enumerate(top, 1):
        text += f"{i}. {html.escape(info.get('name','User'))} - {info.get('points',0)} pts | Wins: {info.get('wins',0)}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def baningame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /Baningame do.")
        return
    target = update.message.reply_to_message.from_user
    add_game_ban(update.effective_chat.id, target.id)
    await update.message.reply_text(f"✅ {mention_user(target)} game se banned.", parse_mode=ParseMode.HTML)

async def unbaningame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /Unbaningame do.")
        return
    target = update.message.reply_to_message.from_user
    remove_game_ban(update.effective_chat.id, target.id)
    await update.message.reply_text(f"✅ {mention_user(target)} game se unbanned.", parse_mode=ParseMode.HTML)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /ban do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"✅ {mention_user(target)} banned.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Ban failed: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /unban do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"✅ {mention_user(target)} unbanned.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Unban failed: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /mute do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(f"✅ {mention_user(target)} muted.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Mute failed: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /unmute do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(f"✅ {mention_user(target)} unmuted.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Unmute failed: {e}")

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    chat_id = update.effective_chat.id

    # Group me /chatbot off hai to sticker reply bhi band
    if update.effective_chat.type in ["group", "supergroup"]:
        if chatbot_status.get(chat_id, True) is False:
            return

    sticker = update.message.sticker

    if sticker and sticker.set_name:
        try:
            sticker_set = await context.bot.get_sticker_set(sticker.set_name)
            random_sticker = random.choice(sticker_set.stickers)
            await update.message.reply_sticker(random_sticker.file_id)
        except Exception as e:
            print("Sticker Error:", e)


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    # ConnectWin active ho to joined players ke normal guesses check honge
    if await connect_guess_handler(update, context):
        return

    # Slash ke bina betting: bbet <amount>
    if await bbet_text_handler(update, context):
        return

    chat_id = update.effective_chat.id

    if update.effective_chat.type in ["group", "supergroup"]:
        if chatbot_status.get(chat_id, True) is False:
            return

        # Group me bot sirf tab reply karega jab user bot ke message ko reply kare
        if not update.message.reply_to_message:
            return

        replied_user = update.message.reply_to_message.from_user
        if not replied_user or replied_user.id != context.bot.id:
            return

    if not client:
        return

    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Ada. Sabse friendly tareeke se baat karo. Hindi me baat karo lekin English alphabets me. Short aur natural replies do. User jaise baat kare waise reply do. Human friend ki tarah behave karo."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply[:4000])

    except Exception as e:
        print("Groq Error:", e)
        await update.message.reply_text("⚠️ AI busy hai, thodi der baad try karo.")


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("chaingamehelp", chaingamehelp))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))
app.add_handler(CommandHandler(["tagall", "Tagall"], tagall))

app.add_handler(CommandHandler("startconnectwin", connectwin))
app.add_handler(CommandHandler("startchaingame", startchaingame))
app.add_handler(CommandHandler("endconnectwin", endconnectwin))
app.add_handler(CommandHandler("join", join_connect))
app.add_handler(CommandHandler("cleaderboard", cleaderboard))
app.add_handler(CommandHandler(["balance", "bal"], balance_cmd))
app.add_handler(CommandHandler("daily", daily_cmd))
app.add_handler(CommandHandler("give", give_cmd))
app.add_handler(CommandHandler(["toprich", "leaderboard"], toprich_cmd))
app.add_handler(CommandHandler("rank", rank_cmd))
app.add_handler(CommandHandler("rob", rob_cmd))
app.add_handler(CommandHandler("kill", kill_cmd))
app.add_handler(CommandHandler("protect", protect_cmd))
app.add_handler(CommandHandler(["shield", "protection"], shield_cmd))
app.add_handler(CommandHandler("revive", revive_cmd))
app.add_handler(CommandHandler("topkill", topkill_cmd))
app.add_handler(CommandHandler("bet", bet_cmd))
app.add_handler(CommandHandler(["games", "game"], games_cmd))
app.add_handler(CommandHandler(["Baningame", "baningame"], baningame))
app.add_handler(CommandHandler(["Unbaningame", "unbaningame"], unbaningame))

app.add_handler(CommandHandler(["ban", "Ban"], ban_user))
app.add_handler(CommandHandler(["unban", "Unban"], unban_user))
app.add_handler(CommandHandler(["mute", "Mute"], mute_user))
app.add_handler(CommandHandler(["unmute", "Unmute"], unmute_user))

app.add_handler(CommandHandler("couples", couples))
app.add_handler(CommandHandler("crush", crush))
app.add_handler(CommandHandler("brain", brain))
app.add_handler(CommandHandler("love", love))

app.add_handler(CommandHandler("slap", slap))
app.add_handler(CommandHandler("kiss", kiss))
app.add_handler(CommandHandler("hug", hug))
app.add_handler(CommandHandler("pat", pat))
app.add_handler(CommandHandler("bite", bite))
app.add_handler(CommandHandler("punch", punch))
app.add_handler(CommandHandler("kill", kill))
app.add_handler(CommandHandler("dance", dance))
app.add_handler(CommandHandler("cry", cry))

app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
app.add_handler(CallbackQueryHandler(help_buttons, pattern="help_"))
app.add_handler(CallbackQueryHandler(hint_button, pattern="opphint:"))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

print("Ada Bot Started...")
app.run_polling()
