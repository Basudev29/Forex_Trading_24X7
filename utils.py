import requests
from datetime import datetime
import feedparser

def fetch_price(symbol, api_key):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"
    try:
        res = requests.get(url, timeout=10).json()
        return float(res.get("price", 0))
    except:
        return None

def generate_signal(price):
    if not price:
        return "⚠ Price unavailable"
    return "Overbought — Possible correction" if price % 2 == 0 else "Oversold — Possible rebound"

def format_response(pair, price):
    signal = generate_signal(price)
    return f"{pair}\nPrice: {price}\nSignal: {signal}\nUpdated: {datetime.utcnow()} UTC"

def fetch_news(rss_url):
    feed = feedparser.parse(rss_url)
    news_items = []
    for entry in feed.entries[:5]:  # last 5 news
        news_items.append(f"{entry.title}\n{entry.link}")
    return news_items

def ai_reply(text):
    # Simple rule-based AI; replace with OpenAI GPT if API available
    text = text.lower()
    if "hello" in text or "hi" in text:
        return "Hello! 🤖 How can I help you today?"
    if "price" in text:
        return "Use /market to get live Forex prices."
    if "news" in text:
        return "Use /news to get latest Forex news."
    return "I am not sure about that. Try /start or /market."
