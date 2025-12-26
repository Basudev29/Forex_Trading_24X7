from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import fetch_price, format_response
from config import TD_API_KEY, ADMIN_IDS, PAIRS
import asyncio

async def daily_market_update(app):
    for admin_id in ADMIN_IDS:
        for name, sym in PAIRS.items():
            price = fetch_price(sym, TD_API_KEY)
            msg = format_response(name, price)
            await app.bot.send_message(chat_id=admin_id, text=msg)

def start_scheduler(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_market_update, "cron", hour=0, args=[app])  # every day at 00:00 UTC
    scheduler.start()
