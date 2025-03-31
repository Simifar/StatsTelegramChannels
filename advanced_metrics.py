from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.utils import get_display_name

async def get_top_posts(messages, client, top_n=3):
    """Возвращает топ постов с корректными ссылками"""
    def engagement(msg):
        reactions = sum(r.count for r in msg.reactions.results) if msg.reactions else 0
        return (msg.views or 0) + reactions

    sorted_msgs = sorted(messages, key=engagement, reverse=True)
    top_msgs = sorted_msgs[:top_n]

    top_posts = []
    for msg in top_msgs:
        try:
            # Получаем информацию о канале
            entity = await msg.get_chat()
            channel_full = await client(GetFullChannelRequest(entity))
            
            # Формируем правильную ссылку
            if entity.username:
                link = f"https://t.me/{entity.username}/{msg.id}"
            else:
                # Для каналов без username используем ID с префиксом /c/
                link = f"https://t.me/c/{entity.id}/{msg.id}"
            
            # Для альбомов используем первое сообщение
            if msg.grouped_id and msg.grouped_id not in [p.get('group_id') for p in top_posts]:
                post_data = {
                    'group_id': msg.grouped_id,
                    'views': msg.views or 0,
                    'reactions': sum(r.count for r in msg.reactions.results) if msg.reactions else 0,
                    'comments': msg.replies.replies if msg.replies else 0,
                    'forwards': msg.forwards or 0,
                    'link': link,
                    'text_preview': (msg.text[:100] + "...") if msg.text else "Медиа-контент",
                    'date': msg.date.astimezone(channel_full.full_chat.chats[0].timezone).strftime("%d.%m.%Y %H:%M")
                }
                top_posts.append(post_data)
            elif not msg.grouped_id:
                top_posts.append({
                    'id': msg.id,
                    'views': msg.views or 0,
                    'reactions': sum(r.count for r in msg.reactions.results) if msg.reactions else 0,
                    'comments': msg.replies.replies if msg.replies else 0,
                    'forwards': msg.forwards or 0,
                    'link': link,
                    'text_preview': (msg.text[:100] + "...") if msg.text else "Медиа-контент",
                    'date': msg.date.astimezone(channel_full.full_chat.chats[0].timezone).strftime("%d.%m.%Y %H:%M")
                })
        
        except Exception as e:
            continue

    return top_posts[:top_n]

def subscriber_growth(current_subs, previous_subs):
    """Рассчитывает рост подписчиков"""
    growth = current_subs - previous_subs
    growth_percent = (growth / previous_subs * 100) if previous_subs else 0
    return {
        'absolute': growth,
        'percent': round(growth_percent, 2),
        'current': current_subs,
        'previous': previous_subs
    }
