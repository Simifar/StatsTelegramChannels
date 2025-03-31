from datetime import datetime, timedelta, time
import pytz
from telethon.tl.functions.channels import GetFullChannelRequest
from advanced_metrics import get_top_posts, subscriber_growth

async def fetch_messages_in_period(client, entity, period_start, period_end, tz, batch_size=100):
    messages = []
    offset_id = 0
    seen_grouped_ids = set()
    grouped_messages = {}

    while True:
        batch = await client.get_messages(entity, limit=batch_size, offset_id=offset_id)
        if not batch:
            break

        for msg in batch:
            if not msg.date:
                continue

            msg_date = msg.date if msg.date.tzinfo else pytz.utc.localize(msg.date)
            msg_date = msg_date.astimezone(tz)

            if msg_date < period_start:
                # Выходим, если достигли сообщения до начала периода
                return messages + list(grouped_messages.values())

            if period_start <= msg_date < period_end:
                if msg.action or (not msg.message and not msg.media and not msg.poll):
                    continue

                # Если это часть альбома
                if msg.grouped_id:
                    # Если уже есть сообщение из группы, то проверим реакции
                    if msg.grouped_id in grouped_messages:
                        existing_msg = grouped_messages[msg.grouped_id]
                        # Если в текущем сообщении больше реакций — обновляем его
                        current_reactions = sum(r.count for r in msg.reactions.results) if msg.reactions else 0
                        existing_reactions = sum(r.count for r in existing_msg.reactions.results) if existing_msg.reactions else 0
                        if current_reactions > existing_reactions:
                            grouped_messages[msg.grouped_id] = msg
                    else:
                        grouped_messages[msg.grouped_id] = msg
                else:
                    messages.append(msg)

        offset_id = batch[-1].id
        if len(batch) < batch_size:
            break

    return messages + list(grouped_messages.values())


async def calculate_metrics(entity, messages, client, days_ago=None, start_date=None, end_date=None, tz=None):
    if tz is None:
        tz = pytz.utc

    now = datetime.now(tz)

    if days_ago is not None:
        period_start = now - timedelta(days=days_ago)
        period_end = now
    elif start_date and end_date:
        period_start = start_date if start_date.tzinfo else tz.localize(start_date)
        period_end = end_date if end_date.tzinfo else tz.localize(end_date)
    else:
        period_start = now - timedelta(days=30)
        period_end = now

    filtered_messages = [
        msg for msg in messages
        if period_start.astimezone(pytz.utc) <= msg.date.astimezone(pytz.utc) < period_end.astimezone(pytz.utc)
    ]

    total_views = sum(msg.views or 0 for msg in filtered_messages)
    total_reactions = sum(
        sum(r.count for r in msg.reactions.results) if msg.reactions else 0
        for msg in filtered_messages
    )
    total_comments = sum(msg.replies.replies if msg.replies and msg.replies.replies else 0 for msg in filtered_messages)
    total_forwards = sum(msg.forwards if msg.forwards else 0 for msg in filtered_messages)

    full_channel = await client(GetFullChannelRequest(entity))
    subscribers = full_channel.full_chat.participants_count

    avg_reach = total_views / len(filtered_messages) if len(filtered_messages) > 0 else 0
    er_percent = ((total_reactions + total_comments + total_forwards) / total_views * 100) if total_views > 0 else 0
    err_percent = (avg_reach / subscribers * 100) if subscribers else 0

    try:
        top_posts = await get_top_posts(filtered_messages, client)
    except Exception as e:
        print(f"Ошибка при получении топ-постов: {str(e)}")
        top_posts = []

    return {
        "subscribers": subscribers,
        "total_posts": len(filtered_messages),
        "total_views": total_views,
        "total_reactions": total_reactions,
        "total_comments": total_comments,
        "total_forwards": total_forwards,
        "avg_reach": round(avg_reach, 2),
        "er_percent": round(er_percent, 2),
        "err_percent": round(err_percent, 2),
        "top_posts": top_posts
    }
