from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для анализа Telegram-каналов.\n"
        "📊 Используй /analyze для анализа.\n"
        "🔐 Доступ только для админов."
    )

@router.message()
async def show_id(message: Message):
    await message.answer(f"🆔 Твой ID: <code>{message.from_user.id}</code>")
