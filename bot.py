import random
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8484299407:AAFgHyNXSHEqrVaij1ocbf6933DGyp7-f-Y"

# -----------------------
# 🃏 카드 덱 (너 파일 기준)
# -----------------------
suits = ["hearts", "diamonds", "clubs", "spades"]
values = [
    "2","3","4","5","6","7","8","9","10",
    "jack","queen","king","ace"
]

deck = [f"{v}_of_{s}" for s in suits for v in values]


# -----------------------
# 🎲 카드 뽑기
# -----------------------
def draw():
    return random.choice(deck)


# -----------------------
# 🎰 점수 계산 (바카라 간단버전)
# -----------------------
def score(cards):
    total = 0
    for c in cards:
        v = c.split("_")[0]
        if v.isdigit():
            total += int(v)
        else:
            total += 0 if v in ["jack","queen","king","ace"] else 0
    return total % 10


# -----------------------
# 🃏 게임 실행
# -----------------------
def game():
    player = [draw(), draw()]
    banker = [draw(), draw()]

    ps = score(player)
    bs = score(banker)

    if ps > bs:
        result = "PLAYER"
    elif bs > ps:
        result = "BANKER"
    else:
        result = "TIE"

    return player, banker, result


# -----------------------
# 🎰 이미지 생성
# -----------------------
def make_image(player, banker, result):
    bg = Image.new("RGB", (900, 500), (0, 120, 0))

    x = 100
    for c in player:
        img = Image.open(f"cards/{c}.png").resize((120,170))
        bg.paste(img, (x, 120))
        x += 140

    x = 500
    for c in banker:
        img = Image.open(f"cards/{c}.png").resize((120,170))
        bg.paste(img, (x, 120))
        x += 140

    path = "result.png"
    bg.save(path)
    return path


# -----------------------
# 🎮 /바카라 명령어
# -----------------------
async def baccarat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    player, banker, result = game()
    img = make_image(player, banker, result)

    await update.message.reply_photo(photo=open(img, "rb"))


# -----------------------
# 🚀 실행
# -----------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("바카라", baccarat))

print("G COIN BOT STARTED")
app.run_polling()
