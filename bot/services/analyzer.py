from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from metrics_calculator import calculate_metrics, fetch_messages_in_period
from telegram_utils import authenticate_client
from bot.config import API_ID, API_HASH, PHONE_NUMBER

TZ = pytz.timezone("Europe/Moscow")

async def analyze_channel(username: str, days: int):
    now = datetime.now(TZ)
    start_date = now - timedelta(days=days)

    async with TelegramClient("bot_session", API_ID, API_HASH) as client:
        if not await client.is_user_authorized():
            await authenticate_client(client, PHONE_NUMBER)

        entity = await client.get_entity(username)
        messages = await fetch_messages_in_period(client, entity, start_date, now, TZ)
        metrics = await calculate_metrics(entity, messages, client, start_date=start_date, end_date=now, tz=TZ)
        metrics["days"] = days
        return metrics