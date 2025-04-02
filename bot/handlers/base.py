from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database.db import create_user, get_user, create_trial_subscription, get_subscription
from bot.config import ADMINS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name

    existing = await get_user(user_id)
    if not existing:
        await create_user(
            user_id=user_id,
            username=username,
            full_name=full_name,
            is_admin=str(user_id) in ADMINS
        )
        await create_trial_subscription(user_id)
        await message.answer(f"👋 Привет, {full_name}! Вы получили пробный период на 3 дня.")
    else:
        sub = await get_subscription(user_id)
        if sub:
            await message.answer("🔓 Подписка активна. Добро пожаловать!")
        else:
            await message.answer("🔒 У вас нет активной подписки. Используйте /subscribe")