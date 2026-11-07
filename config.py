
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()

# Admins
ADMIN_IDS = [
    int(item.strip())
    for item in os.getenv("ADMIN_IDS", "").split(",")
    if item.strip().isdigit()
]

# Database
DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "vindora_bot.db"
).strip()

# Validation
if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN is missing.")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is missing.")

if not ADMIN_IDS:
    print("WARNING: No ADMIN_IDS configured.")
