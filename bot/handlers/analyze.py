from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from ..config import ADMINS

router = Router()

@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    if str(message.from_user.id) not in ADMINS:
        return await message.answer("🚫 Доступ запрещён.")
    
    await message.answer("📊 Анализ с кнопками в разработке (заглушка).")