from telegram import Update
from utils import get_economic_calendar
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, TD_API_KEY, ADMIN_IDS, NEWS_RSS_URL
from utils import fetch_price, format_response, fetch_news, ai_reply
from db import init_db, add_or_update_user
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "GOLD": "XAU/USD"
}

# Initialize DB
init_db()

# ----- Commands -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username, user.first_name, user.last_name, "/start")
    await update.message.reply_text("🤖 ForexTrading24x7 Bot Active\nUse /market, /news, /calendar")

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username, user.first_name, user.last_name, "/market")
    for name, sym in PAIRS.items():
        price = fetch_price(sym, TD_API_KEY)
        await update.message.reply_text(format_response(name, price))

async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username, user.first_name, user.last_name, "/calendar")
    await update.message.reply_text(get_economic_calendar())

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username, user.first_name, user.last_name, "/news")
    items = fetch_news(NEWS_RSS_URL)
    if not items:
        await update.message.reply_text("⚠ News feed not available")
        return
    for item in items:
        await update.message.reply_text(item)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user.id, user.username, user.first_name, user.last_name, "text")
    await update.message.reply_text(ai_reply(update.message.text))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Not authorized")
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("Provide a message")
        return
    for user_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=user_id, text=f"📢 Broadcast: {msg}")
    await update.message.reply_text("✅ Broadcast sent")

# ----- Scheduler -----
async def daily_update(app):
    for admin_id in ADMIN_IDS:
        for name, sym in PAIRS.items():
            price = fetch_price(sym, TD_API_KEY)
            await app.bot.send_message(chat_id=admin_id, text=format_response(name, price))

def start_scheduler(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(daily_update(app)), "cron", hour=0)  # daily UTC 00:00
    scheduler.start()

# ----- Main -----
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("calendar", calendar))

    # Auto reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


    # Start scheduler
    start_scheduler(app)

    print("🚀 Bot Started — Polling...")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
