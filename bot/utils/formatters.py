def format_stats(metrics: dict) -> str:
    return (
        f"<b>📊 Статистика за {metrics['days']} дней</b>\n"
        f"👥 Подписчики: <b>{metrics['subscribers']}</b>\n"
        f"📝 Посты: {metrics['total_posts']}\n"
        f"👀 Просмотры: {metrics['total_views']}\n"
        f"❤️ Реакции: {metrics['total_reactions']}\n"
        f"💬 Комментарии: {metrics['total_comments']}\n"
        f"↩️ Репосты: {metrics['total_forwards']}\n"
        f"📈 ER: <b>{metrics['er_percent']}%</b>\n"
        f"🎯 ERR: <b>{metrics['err_percent']}%</b>\n"
        f"\n🔥 <i>Топ посты:</i>\n" +
        "\n".join(
            f"<a href='{post['link']}'>🔗 Пост {post['id']}</a> — 👀 {post['views']} ❤️ {post['reactions']} 💬 {post['comments']}"
            for post in metrics.get("top_posts", [])[:3]
        )
    )
