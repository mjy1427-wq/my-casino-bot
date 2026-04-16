import random
import json
import os
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8484299407:AAFgHyNXSHEqrVaij1ocbf6933DGyp7-f-Y"
ADMIN_ID = 7476630349
DB_FILE = "db.json"

# =========================
# 💾 DB
# =========================
def load_db():
    if not os.path.exists(DB_FILE):
        return {"vault": 1000000, "users": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def get_user(db, uid):
    if uid not in db["users"]:
        db["users"][uid] = {
            "balance": 1000000,
            "inventory": {},
            "joined": "2026-01-01"
        }
    return db["users"][uid]

# =========================
# 🪨 광물 / 곡괭이
# =========================
ORES = {
    "stone": {"tier": 1, "price": 1000},
    "iron": {"tier": 2, "price": 5000},
    "gold": {"tier": 3, "price": 20000},
    "diamond": {"tier": 4, "price": 100000}
}

PICKAXE_SHOP = {
    "Wood": {"price": 1000000, "durability": 100, "mult": 1.0, "rate_bonus": 0},
    "Stone": {"price": 5000000, "durability": 300, "mult": 1.5, "rate_bonus": 5},
    "Iron": {"price": 15000000, "durability": 500, "mult": 2.0, "rate_bonus": 10},
    "Gold": {"price": 50000000, "durability": 1000, "mult": 3.0, "rate_bonus": 20},
    "Diamond": {"price": 250000000, "durability": 5000, "mult": 5.0, "rate_bonus": 35},
    "Orichalcon": {"price": 1000000000, "durability": 10000, "mult": 10.0, "rate_bonus": 60}
}

# =========================
# 👤 가입
# =========================
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    uid = str(update.effective_user.id)

    if uid not in db["users"]:
        db["users"][uid] = {
            "balance": 1000000,
            "inventory": {},
            "joined": str(update.message.date)
        }
        save_db(db)

    await update.message.reply_text("✅ 가입 완료 + 1,000,000 지급")

# =========================
# 💰 내정보
# =========================
async def myinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    uid = str(update.effective_user.id)
    user = get_user(db, uid)

    await update.message.reply_text(
        f"👤 ID: {uid}\n"
        f"💰 GCOIN: {user['balance']}\n"
        f"📅 가입일: {user['joined']}"
    )

# =========================
# ⛏ 채광
# =========================
async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = load_db()
    uid = str(update.effective_user.id)
    user = get_user(db, uid)

    inv = user.setdefault("inventory", {})

    pickaxe = "Wood"
    for p in PICKAXE_SHOP:
        if p in inv:
            pickaxe = p
            break

    data = PICKAXE_SHOP[pickaxe]

    if random.randint(1, 100) <= 5 + data["rate_bonus"]:
        ore = "diamond"
    else:
        ore = random.choice(["stone", "iron", "gold"])

    amount = int(random.randint(1, 5) * data["mult"])

    inv[ore] = inv.get(ore, 0) + amount

    if pickaxe in inv:
        inv[pickaxe]["durability"] -= 1

    user["inventory"] = inv
    save_db(db)

    ore_data = ORES[ore]

    await update.message.reply_text(
        f"⛏ 채광 성공!\n"
        f"광물: {ore.upper()} (N{ore_data['tier']})\n"
        f"가격: {ore_data['price']}\n"
        f"곡괭이: {pickaxe}\n"
        f"내구도: {inv[pickaxe]['durability'] if pickaxe in inv else 0}"
    )

# =========================
# 🎒 인벤
# =========================
async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    uid = str(update.effective_user.id)
    user = get_user(db, uid)

    inv = user.get("inventory", {})

    text = "🎒 INVENTORY\n\n"
    for k, v in inv.items():
        text += f"{k}: {v}\n"

    await update.message.reply_text(text)

# =========================
# 🏆 랭킹
# =========================
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()

    users = db["users"]
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)

    text = "🏆 TOP 10\n\n"
    for i, (uid, u) in enumerate(sorted_users[:10]):
        title = "KING" if i == 0 else "TOP"
        text += f"{i+1}. {uid} - {u['balance']} ({title})\n"

    await update.message.reply_text(text)

# =========================
# 💸 송금
# =========================
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()

    uid = str(update.effective_user.id)
    user = get_user(db, uid)

    target = context.args[0]
    amount = int(context.args[1])

    tuser = get_user(db, target)

    if user["balance"] < amount:
        return await update.message.reply_text("잔액 부족")

    user["balance"] -= amount
    tuser["balance"] += amount

    save_db(db)

    await update.message.reply_text("송금 완료")

# =========================
# 🛒 상점
# =========================
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = "⛏ SHOP\n선택하세요"

    keyboard = [
        [InlineKeyboardButton("Wood", callback_data="buy_Wood")],
        [InlineKeyboardButton("Stone", callback_data="buy_Stone")],
        [InlineKeyboardButton("Iron", callback_data="buy_Iron")],
        [InlineKeyboardButton("Gold", callback_data="buy_Gold")],
        [InlineKeyboardButton("Diamond", callback_data="buy_Diamond")],
        [InlineKeyboardButton("Orichalcon", callback_data="buy_Orichalcon")]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# =========================
# 🛒 구매
# =========================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    db = load_db()
    uid = str(query.from_user.id)
    user = get_user(db, uid)

    item = query.data.replace("buy_", "")
    data = PICKAXE_SHOP[item]

    if user["balance"] < data["price"]:
        return await query.message.reply_text("❌ 돈 부족")

    user["balance"] -= data["price"]

    inv = user.setdefault("inventory", {})
    if item in inv:
        inv[item]["durability"] += data["durability"]
    else:
        inv[item] = {"durability": data["durability"]}

    save_db(db)

    await query.message.reply_text(f"✅ 구매 완료 {item}")

# =========================
# 🚀 RUN
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("가입", join))
app.add_handler(CommandHandler("내정보", myinfo))
app.add_handler(CommandHandler("채광", mine))
app.add_handler(CommandHandler("인벤", inventory))
app.add_handler(CommandHandler("랭킹", ranking))
app.add_handler(CommandHandler("송금", send))
app.add_handler(CommandHandler("상점", shop))
app.add_handler(CallbackQueryHandler(buy))

print("BOT STARTED")
app.run_polling()
