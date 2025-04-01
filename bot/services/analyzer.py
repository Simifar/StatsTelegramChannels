from datetime import datetime, timedelta
import pytz
from metrics_calculator import calculate_metrics, fetch_messages_in_period

TZ_MOSCOW = pytz.timezone("Europe/Moscow")

async def analyze_channel(client, username: str, days: int):
    entity = await client.get_entity(username)
    now = datetime.now(TZ_MOSCOW)
    period_start = now - timedelta(days=days)

    messages = await fetch_messages_in_period(
        client, entity, period_start, now, TZ_MOSCOW
    )

    metrics = await calculate_metrics(
        entity=entity,
        messages=messages,
        client=client,
        days_ago=days,
        tz=TZ_MOSCOW
    )
    metrics["days"] = days
    return metrics
