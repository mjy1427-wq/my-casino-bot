import random
import json
from PIL import Image, ImageDraw
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8484299407:AAFgHyNXSHEqrVaij1ocbf6933DGyp7-f-Y"
DB_FILE = "db.json"

# =========================
# 💾 DB 로드/저장
# =========================
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"vault": 1000000, "users": {}}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)


# =========================
# 🃏 카드 덱
# =========================
suits = ["hearts", "diamonds", "clubs", "spades"]
values = ["2","3","4","5","6","7","8","9","10","jack","queen","king","ace"]
deck = [f"{v}_of_{s}" for s in suits for v in values]


# =========================
# 🎲 카드
# =========================
def draw():
    return random.choice(deck)


def score(cards):
    total = 0
    for c in cards:
        v = c.split("_")[0]
        total += int(v) if v.isdigit() else 0
    return total % 10


# =========================
# 🎰 바카라 (3rd card 포함)
# =========================
def baccarat_game():
    player = [draw(), draw()]
    banker = [draw(), draw()]

    ps = score(player)
    bs = score(banker)

    player_third = None

    # PLAYER 3rd card
    if ps <= 5:
        player_third = draw()
        player.append(player_third)
        ps = score(player)

    # BANKER rule (단순화)
    if bs <= 5:
        banker.append(draw())
        bs = score(banker)

    if ps > bs:
        result = "PLAYER"
    elif bs > ps:
        result = "BANKER"
    else:
        result = "TIE"

    return player, banker, result


# =========================
# 🖼 이미지 생성
# =========================
def make_image(player, banker, result):
    bg = Image.new("RGB", (900, 500), (0, 120, 0))
    draw = ImageDraw.Draw(bg)

    draw.text((350, 20), "G COIN CASINO", fill=(255,255,255))

    # PLAYER
    x = 80
    draw.text((80, 80), "PLAYER", fill=(255,255,255))
    for c in player:
        img = Image.open(f"cards/{c}.png").resize((110,160))
        bg.paste(img, (x, 120))
        x += 130

    # BANKER
    x = 500
    draw.text((500, 80), "BANKER", fill=(255,255,255))
    for c in banker:
        img = Image.open(f"cards/{c}.png").resize((110,160))
        bg.paste(img, (x, 120))
        x += 130

    draw.text((350, 430), f"RESULT: {result}", fill=(255,255,0))

    path = "result.png"
    bg.save(path)
    return path


# =========================
# 💰 유저 생성
# =========================
def get_user(db, user_id):
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "balance": 10000,
            "inventory": {}
        }
    return db["users"][user_id]


# =========================
# 🎮 바카라 명령어
# =========================
async def baccarat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = str(update.effective_user.id)
    user = get_user(db, user_id)

    player, banker, result = baccarat_game()
    img = make_image(player, banker, result)

    # 💰 간단 베팅 처리 (기본 1000)
    bet = 1000

    if result == "PLAYER":
        user["balance"] += bet
    elif result == "BANKER":
        user["balance"] += int(bet * 0.95)
    else:
        user["balance"] += bet * 8

    save_db(db)

    await update.message.reply_photo(
        photo=open(img, "rb"),
        caption=f"🎰 {result}\n💰 BALANCE: {user['balance']}"
    )


# =========================
# ⛏ 채광
# =========================
async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = str(update.effective_user.id)
    user = get_user(db, user_id)

    items = ["gold", "silver", "iron"]
    item = random.choice(items)

    user["inventory"][item] = user["inventory"].get(item, 0) + 1
    save_db(db)

    await update.message.reply_text(f"⛏ 획득: {item}")


# =========================
# 💸 송금
# =========================
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()

    user_id = str(update.effective_user.id)
    user = get_user(db, user_id)

    if len(context.args) < 2:
        return await update.message.reply_text("사용법: .송금 ID 금액")

    target = context.args[0]
    amount = int(context.args[1])

    target_user = get_user(db, target)

    if user["balance"] < amount:
        return await update.message.reply_text("잔액 부족")

    user["balance"] -= amount
    target_user["balance"] += amount

    save_db(db)

    await update.message.reply_text("송금 완료")


# =========================
# 🚀 실행
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("바카라", baccarat))
app.add_handler(CommandHandler("채광", mine))
app.add_handler(CommandHandler("송금", send))

print("G COIN CASINO STARTED")
app.run_polling()
