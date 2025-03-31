from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.utils import get_peer_id

async def get_top_posts(messages, client, top_n=3):
    """Возвращает топ постов с корректными ссылками"""
    if not messages:
        return []

    def engagement(msg):
        reactions = sum(r.count for r in msg.reactions.results) if msg.reactions else 0
        return (msg.views or 0) + reactions

    sorted_msgs = sorted(messages, key=engagement, reverse=True)
    top_msgs = sorted_msgs[:top_n]

    top_posts = []
    for msg in top_msgs:
        try:
            entity = await msg.get_chat()
            full_channel = await client(GetFullChannelRequest(entity))
            
            # Формирование ссылки
            if entity.username:
                link = f"https://t.me/{entity.username}/{msg.id}"
            else:
                channel_id = get_peer_id(entity)
                link = f"https://t.me/c/{abs(channel_id)}/{msg.id}"

            post_data = {
                'id': msg.id,
                'views': msg.views or 0,
                'reactions': sum(r.count for r in msg.reactions.results) if msg.reactions else 0,
                'comments': msg.replies.replies if msg.replies else 0,
                'forwards': msg.forwards or 0,
                'link': link,
                'text_preview': (msg.text[:100] + "...") if msg.text else "Медиа-контент"
            }
            
            top_posts.append(post_data)
            
        except Exception as e:
            continue

    return top_posts[:top_n]

def subscriber_growth(current_subs, previous_subs):
    growth = current_subs - previous_subs
    growth_percent = (growth / previous_subs * 100) if previous_subs else 0
    return {
        'absolute': growth,
        'percent': round(growth_percent, 2),
        'current': current_subs,
        'previous': previous_subs
    }