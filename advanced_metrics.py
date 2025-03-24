from telethon.tl.functions.channels import GetFullChannelRequest

# advanced_metrics.py
async def get_top_posts(messages, top_n=3):
    def engagement(msg):
        reactions = sum(r.count for r in msg.reactions.results) if msg.reactions else 0
        return (msg.views or 0) + reactions

    sorted_msgs = sorted(messages, key=engagement, reverse=True)
    top_msgs = sorted_msgs[:top_n]

    return [{
        'id': msg.id,
        'views': msg.views or 0,
        'reactions': sum(r.count for r in msg.reactions.results) if msg.reactions else 0,
        'comments': msg.replies.replies if msg.replies else 0,
        'forwards': msg.forwards or 0,
        'link': f"https://t.me/{msg.peer_id.channel_id}/{msg.id}",
        'text_preview': (msg.message[:100] + "...") if msg.message else "Нет текста"
    } for msg in top_msgs]


def subscriber_growth(current_subs, previous_subs):
    growth = current_subs - previous_subs
    growth_percent = (growth / previous_subs * 100) if previous_subs else 0
    return growth, round(growth_percent, 2)
