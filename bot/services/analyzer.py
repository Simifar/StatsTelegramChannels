from datetime import datetime, timedelta
import pytz
from telethon.tl.functions.channels import GetFullChannelRequest
from ..metrics_calculator import calculate_metrics

async def analyze_channel(client, channel: str, days: int):
    """Анализ канала за указанный период"""
    try:
        entity = await client.get_entity(channel)
        period_end = datetime.now(pytz.utc)
        period_start = period_end - timedelta(days=days)
        
        messages = await client.get_messages(
            entity,
            limit=None,
            offset_date=period_end
        )
        
        return await calculate_metrics(
            entity=entity,
            messages=messages,
            client=client,
            days_ago=days
        )
        
    except Exception as e:
        raise RuntimeError(f"Ошибка анализа: {str(e)}")