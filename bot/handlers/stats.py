from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from ..services.analyzer import analyze_channel
from ..utils.formatters import format_stats
from ..config import ADMINS

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if str(message.from_user.id) not in ADMINS:
        return await message.answer("🚫 Только админы могут использовать этот бот.")

    args = message.text.split()
    if len(args) != 3:
        return await message.answer(
            "❌ Формат: <code>/stats username N_дней</code>\n"
            "Пример: <code>/stats rezumus 7</code>",
            parse_mode=ParseMode.HTML
        )

    username = args[1]
    try:
        days = int(args[2])
    except ValueError:
        return await message.answer("❌ Укажите корректное число дней!")

    try:
        metrics = await analyze_channel(username, days)
        await message.answer(format_stats(metrics), disable_web_page_preview=True)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")