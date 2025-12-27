import os
import requests
import telebot
import threading
import time

# -------- CONFIG --------
BOT_TOKEN = os.getenv("BOT_TOKEN")
TD_API_KEY = os.getenv("TWELVEDATA_API_KEY")

ADMIN_IDS = [966554382945]   # your telegram id
CHAT_ID = None

bot = telebot.TeleBot(BOT_TOKEN)

PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "XAU/USD": "XAU/USD"
}


# -------- PRICE FETCH --------
def get_live_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TD_API_KEY}"
    try:
        r = requests.get(url, timeout=10).json()
        if "price" in r:
            return float(r["price"])
        return None
    except:
        return None


def generate_signal(price, support, resistance):
    if price is None:
            return "⚠ Live price not available"

    if price < support:
        bias = "Oversold — Possible Bounce"
    elif price > resistance:
        bias = "Overbought — Possible Correction"
    else:
        bias = "Neutral — Range Zone"

    return f"""
Price: {price}
Support: {support}
Resistance: {resistance}
Signal: {bias}
"""


# -------- PAIR HANDLERS --------
def eurusd():
    p = get_live_price("EUR/USD")
    return "📈 EUR/USD\n" + generate_signal(p, 1.0830, 1.0920)

def gbpusd():
    p = get_live_price("GBP/USD")
    return "💷 GBP/USD\n" + generate_signal(p, 1.2650, 1.2790)

def usdjpy():
    p = get_live_price("USD/JPY")
    return "💹 USD/JPY\n" + generate_signal(p, 150.50, 152.40)

def gold():
    p = get_live_price("XAU/USD")
    return "🏆 GOLD XAU/USD\n" + generate_signal(p, 2358, 2395)


# -------- NEWS (SAFE FALLBACK) --------
def get_news():
    return "📰 News service will be added soon."


# -------- ECONOMIC CALENDAR --------
def economic_calendar():
    return """
📆 Economic Calendar (Today)

• USD — Core PCE Data
• EUR — Consumer Confidence
• GBP — GDP Flash Estimate
• JPY — BOJ Outlook Report
"""


# -------- AUTO DAILY BROADCAST --------
def auto_push():
    while True:
        if CHAT_ID:
            bot.send_message(CHAT_ID, "📊 Daily Market Overview")
            bot.send_message(CHAT_ID, eurusd())
            bot.send_message(CHAT_ID, gbpusd())
            bot.send_message(CHAT_ID, usdjpy())
            bot.send_message(CHAT_ID, gold())
            bot.send_message(CHAT_ID, economic_calendar())
        time.sleep(60 * 60 * 12)  # every 12 hours


threading.Thread(target=auto_push, daemon=True).start()


# -------- MENU UI --------
def menu(chat):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📈 EUR/USD", "💷 GBP/USD")
    kb.add("🏆 GOLD", "💹 USD/JPY")
    kb.add("📊 Full Market Update")
    kb.add("📆 Economic Calendar")
    bot.send_message(chat.id, "Select option 👇", reply_markup=kb)


# -------- COMMANDS --------
@bot.message_handler(commands=["start"])
def start(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(message.chat.id, "🤖 Forex Bot Activated")
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
    elif msg.text == "📊 Full Market Update":
        bot.send_message(msg.chat.id, eurusd())
        bot.send_message(msg.chat.id, gbpusd())
        bot.send_message(msg.chat.id, usdjpy())
        bot.send_message(msg.chat.id, gold())
    elif msg.text == "📆 Economic Calendar":
        bot.send_message(msg.chat.id, economic_calendar())
    else:
        menu(msg.chat)


bot.infinity_polling()
