from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import fetch_price, format_response
from config import TD_API_KEY, ADMIN_IDS, PAIRS
import asyncio

def start_scheduler(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(daily_update(app)), "cron", hour=0)
    scheduler.add_job(lambda: asyncio.create_task(daily_calendar_update(app)), "cron", hour=0, minute=15)

    # Fix: ensure scheduler has an event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    scheduler.start()
