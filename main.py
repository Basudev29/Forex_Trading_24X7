import os
from db import init_db, add_or_update_user
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, TD_API_KEY, ADMIN_IDS, NEWS_RSS_URL
from utils import fetch_price, format_response, fetch_news
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import telebot
import requests
import threading
import time

# --------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"

# ----------------- CONFIG -----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
TD_API_KEY = os.getenv("TWELVEDATA_API_KEY")
ADMIN_IDS = [+966554382945]  # Telegram ID of admin

bot = telebot.TeleBot(BOT_TOKEN)
CHAT_ID = None

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD"]


# ----- Scheduler -----
def start_scheduler(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(daily_update(app)), "cron", hour=0)
    scheduler.start()

async def daily_update(app):
    for admin_id in ADMIN_IDS:
        for name, sym in PAIRS.items():
            price = fetch_price(sym, TD_API_KEY)
            await app.bot.send_message(chat_id=admin_id, text=format_response(name, price))


# ----------------- LIVE PRICE FUNCTION -----------------
def get_live_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TD_API_KEY}"
    try:
        r = requests.get(url, timeout=10).json()
        print("API response:", r)  # Debug
        if "price" in r:
            return float(r["price"])
        elif "message" in r:
            return f"API Error: {r['message']}"
        else:
            return None
    except Exception as e:
        print("Request Error:", e)
        return None

# ----------------- SIGNAL GENERATOR -----------------
def generate_signal(price, support, resistance):
    if price is None or isinstance(price, str):
        return f"⚠ {price or 'Live price not available'}"
    if price < support:
        bias = "Oversold — Possible Bounce"
    elif price > resistance:
        bias = "Overbought — Possible Correction"
    else:
        bias = "Neutral — Range Zone"
    return f"Price: {price}\nSupport: {support}\nResistance: {resistance}\nSignal: {bias}"

# ----------------- PAIR HANDLERS -----------------
def eurusd():
    price = get_live_price("EUR/USD")
    return f"📈 EUR/USD — Live Update\n\n{generate_signal(price, 1.0830, 1.0920)}"

def gbpusd():
    price = get_live_price("GBP/USD")
    return f"💷 GBP/USD — Live Update\n\n{generate_signal(price, 1.2650, 1.2790)}"

def usdjpy():
    price = get_live_price("USD/JPY")
    return f"💹 USD/JPY — Live Update\n\n{generate_signal(price, 150.50, 152.40)}"

def gold():
    price = get_live_price("XAU/USD")
    return f"🏆 GOLD XAU/USD — Live Update\n\n{generate_signal(price, 2358, 2395)}"

# ----------------- NEWS FETCH (Placeholder) -----------------
def get_news():
    try:
        # Free news API placeholder
        url = "https://newsdata.io/api/1/news?category=business,finance&apikey=pub_1234567890"
        r = requests.get(url).json()
        headlines = []
        for a in r.get("results", [])[:4]:
            headlines.append("• " + a["title"])
        return "📰 Market News\n\n" + "\n".join(headlines)
    except:
        return "⚠ News feed not available"

# ----------------- ECONOMIC CALENDAR -----------------
def economic_calendar():
    return """
📆 Economic Calendar (Today)

• USD — Core PCE Data
• EUR — Consumer Confidence
• GBP — GDP Flash Estimate
• JPY — BOJ Outlook Report

⚠ High impact events → Expect volatility
"""

# ----------------- AUTO DAILY BROADCAST -----------------
def auto_push():
    while True:
        if CHAT_ID:
            bot.send_message(CHAT_ID, "📊 Daily Market Overview")
            bot.send_message(CHAT_ID, eurusd())
            bot.send_message(CHAT_ID, gbpusd())
            bot.send_message(CHAT_ID, usdjpy())
            bot.send_message(CHAT_ID, gold())
            bot.send_message(CHAT_ID, get_news())
            bot.send_message(CHAT_ID, economic_calendar())
        time.sleep(60 * 60 * 12)  # every 12 hours

threading.Thread(target=auto_push, daemon=True).start()

# ----------------- MENU BUTTONS -----------------
def menu(chat):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📈 EUR/USD", "💷 GBP/USD")
    kb.add("🏆 GOLD", "💹 USD/JPY")
    kb.add("📰 News", "📆 Economic Calendar")
    kb.add("📊 Full Market Update")
    bot.send_message(chat.id, "Select option 👇", reply_markup=kb)

# ----------------- COMMANDS -----------------
@bot.message_handler(commands=['start'])
def start(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(message.chat.id,
                     "👋 ForexTrading24x7 — Advanced Auto Bot Activated")
    menu(message.chat)

@bot.message_handler(func=lambda m: True)
def buttons(msg):
    if msg.text == "📈 EUR/USD":
        bot.send_message(msg.chat.id, eurusd())
    elif msg.text == "💷 GBP/USD":
        bot.send_message(msg.chat.id, gbpusd())
    elif msg.text == "💹 USD/JPY":
        bot.send_message(msg.chat.id, usdjpy())
    elif msg.text == "🏆 GOLD":
        bot.send_message(msg.chat.id, gold())
    elif msg.text == "📰 News":
        bot.send_message(msg.chat.id, get_news())
    elif msg.text == "📆 Economic Calendar":
        bot.send_message(msg.chat.id, economic_calendar())
    elif msg.text == "📊 Full Market Update":
        bot.send_message(msg.chat.id, eurusd())
        bot.send_message(msg.chat.id, gbpusd())
        bot.send_message(msg.chat.id, usdjpy())
        bot.send_message(msg.chat.id, gold())
        bot.send_message(msg.chat.id, get_news())
        bot.send_message(msg.chat.id, economic_calendar())
    else:
        menu(msg.chat)

bot.infinity_polling()
