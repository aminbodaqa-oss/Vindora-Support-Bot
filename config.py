# config.py
import os

def _parse_admin_ids(value):
    result = set()
    for item in (value or "").replace(";", ",").split(","):
        item = item.strip()
        if item.isdigit():
            result.add(int(item))
    return result

# لا تضع المفاتيح السرية داخل هذا الملف أو GitHub.
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
DATABASE_NAME = os.getenv("DATABASE_NAME", "vindora.db")
