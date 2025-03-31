from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from telethon import TelegramClient
from ..services.analyzer import analyze_channel
from ..utils.formatters import format_stats

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.answer(
                "❌ Формат: <code>/stats канал дней</code>\n"
                "Пример: <code>/stats rezumus 7</code>",
                parse_mode=ParseMode.HTML
            )
            
        async with TelegramClient(...) as client:
            metrics = await analyze_channel(
                client=client,
                channel=args[1],
                days=int(args[2])
            )
            
            await message.answer(
                format_stats(metrics),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")