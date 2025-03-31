import os
import asyncio
import pytz
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from telethon import TelegramClient
from metrics_calculator import fetch_messages_in_period, calculate_metrics
from telegram_utils import authenticate_client

load_dotenv()

# Конфигурация
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
TZ_MOSCOW = pytz.timezone("Europe/Moscow")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def collect_stats(client, channel_username, days_ago):
    """Сбор статистики без использования core.py"""
    try:
        entity = await client.get_entity(channel_username)
        period_end = datetime.now(TZ_MOSCOW)
        period_start = period_end - timedelta(days=days_ago)
        
        messages = await fetch_messages_in_period(
            client, entity, 
            period_start, 
            period_end, 
            TZ_MOSCOW
        )
        
        return await calculate_metrics(
            entity=entity,
            messages=messages,
            client=client,
            days_ago=days_ago,
            tz=TZ_MOSCOW
        )
        
    except Exception as e:
        raise e

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для анализа Telegram-каналов.\n"
        "Доступные команды:\n"
        "/stats <канал> <дней> - статистика за N дней\n"
        "/top_posts <канал> - топ-3 поста\n"
    )

@dp.message(Command("stats"))
async def get_stats(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 3:
            await message.answer("❌ Формат: /stats <username_канала> <дней>")
            return

        channel = args[1]
        days = int(args[2])

        async with TelegramClient('bot_session', API_ID, API_HASH) as client:
            await authenticate_client(client, PHONE_NUMBER)
            metrics = await collect_stats(client, channel, days)

            response = (
                f"📊 Статистика за {days} дней:\n"
                f"👥 Подписчики: {metrics['subscribers']}\n"
                f"📝 Посты: {metrics['total_posts']}\n"
                f"👀 Просмотры: {metrics['total_views']}\n"
                f"❤️ Реакции: {metrics['total_reactions']}\n"
                f"💬 Комментарии: {metrics['total_comments']}\n"
                f"↩️ Репосты: {metrics['total_forwards']}\n"
                f"📈 ER: {metrics['er_percent']}%\n"
                f"🎯 ERR: {metrics['err_percent']}%"
            )
            await message.answer(response)

    except ValueError:
        await message.answer("❌ Некорректное число дней!")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())