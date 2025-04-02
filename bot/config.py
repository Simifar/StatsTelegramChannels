import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
ADMINS = os.getenv("ADMINS", "").split(",")

if not all([BOT_TOKEN, API_ID, API_HASH, PHONE_NUMBER]):
    raise RuntimeError("❌ Не заданы переменные окружения в .env")