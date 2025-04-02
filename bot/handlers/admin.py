from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from ..config import ADMINS

router = Router()

@router.message(Command("import"))
async def import_data(message: Message):
    if str(message.from_user.id) not in ADMINS:
        return await message.answer("🚫 У вас нет доступа к этой команде.")
    
    await message.answer("📥 Импорт данных в разработке (заглушка).")