import streamlit as st
import asyncio
import nest_asyncio
from datetime import datetime, timedelta, time
import pytz
import pandas as pd
from telethon import TelegramClient
from telegram_utils import authenticate_client
from metrics_calculator import calculate_metrics, fetch_messages_in_period
from advanced_metrics import get_top_posts
from dotenv import load_dotenv
import os

load_dotenv()
nest_asyncio.apply()

# Конфигурация
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
TZ_MOSCOW = pytz.timezone("Europe/Moscow")

async def collect_stats(channels, period_start, period_end):
    client = None
    try:
        client = TelegramClient('streamlit_session', API_ID, API_HASH)
        await client.connect()  # Явное подключение
        
        if not await client.is_user_authorized():
            await authenticate_client(client, PHONE_NUMBER)
        
        metrics_all = []
        for channel_username in channels:
            entity = await client.get_entity(channel_username)
            messages = await fetch_messages_in_period(client, entity, period_start, period_end, TZ_MOSCOW)
            metrics = await calculate_metrics(entity, messages, client, start_date=period_start, end_date=period_end, tz=TZ_MOSCOW)
            metrics['Канал'] = channel_username
            metrics['top_posts'] = await get_top_posts(messages)
            metrics_all.append(metrics)
        
        return metrics_all
    finally:
        if client and client.is_connected():
            await client.disconnect()

# ... остальная часть интерфейса без изменений ...

# Интерфейс
st.set_page_config(page_title="Telegram Analytics", layout="wide")
st.title("📊 Аналитика Telegram-каналов")

# Загрузка каналов
with open('channels.txt', 'r', encoding='utf-8') as f:
    channels_list = [line.strip() for line in f if line.strip()]

channels = st.multiselect("Выберите каналы", channels_list, default=channels_list)

# Выбор периода
period_choice = st.radio("Период анализа:", ["Последние N дней", "Диапазон дат", "Месяц"])
now = datetime.now(TZ_MOSCOW)

if period_choice == "Последние N дней":
    days_ago = st.number_input("Количество дней:", min_value=1, max_value=365, value=7)
    period_start = now - timedelta(days=days_ago)
    period_end = now
elif period_choice == "Диапазон дат":
    start = st.date_input("Начало периода", now.date() - timedelta(days=7))
    end = st.date_input("Конец периода:", now.date())
    period_start = TZ_MOSCOW.localize(datetime.combine(start, time.min))
    period_end = TZ_MOSCOW.localize(datetime.combine(end, time.max))
elif period_choice == "Месяц":
    month_choice = st.text_input("Месяц (YYYY-MM)", now.strftime('%Y-%m'))
    year, month = map(int, month_choice.split('-'))
    period_start = TZ_MOSCOW.localize(datetime(year, month, 1))
    period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

if st.button("🚀 Собрать статистику"):
    with st.spinner("Идёт сбор данных..."):
        try:
            stats = asyncio.run(collect_stats(channels, period_start, period_end))
            df = pd.DataFrame(stats)
            
            # Основная таблица
            st.subheader("📌 Общая статистика")
            st.dataframe(df[['Канал', 'subscribers', 'total_posts', 'total_views', 
                           'total_reactions', 'total_comments', 'total_forwards', 
                           'avg_reach', 'er_percent', 'err_percent']])
            
            # Экспорт
            st.subheader("📤 Экспорт данных")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Скачать CSV",
                data=csv,
                file_name="telegram_stats.csv",
                mime="text/csv"
            )
            
            # Топ посты
            st.subheader("🔥 Топ посты")
            for metric in stats:
                st.markdown(f"### 📢 {metric['Канал']}")
                for idx, post in enumerate(metric['top_posts'], 1):
                    st.markdown(f"{idx}. [Пост]({post['link']}) 👀 {post['views']} | 👍 {post['reactions']} | 💬 {post['comments']}")
            
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")