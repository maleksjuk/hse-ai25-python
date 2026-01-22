import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WHEATHER_API_KEY = os.getenv("WHEATHER_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found")
TOKEN = str(TOKEN)
