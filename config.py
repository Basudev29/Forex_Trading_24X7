import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

TD_API_KEY = os.getenv("TWELVEDATA_API_KEY")
