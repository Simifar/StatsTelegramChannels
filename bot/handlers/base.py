from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для анализа Telegram-каналов.\n"
        "📊 Используй команду:\n"
        "<code>/stats username_канала N_дней</code>\n"
        "Пример: <code>/stats rezumus 7</code>"
    )
