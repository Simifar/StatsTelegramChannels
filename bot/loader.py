from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from telethon import TelegramClient
from config import BOT_TOKEN, API_ID, API_HASH

# aiogram
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher(storage=MemoryStorage())

# Telethon client
telethon_client = TelegramClient("bot_session", API_ID, API_HASH)
