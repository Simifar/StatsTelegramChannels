import asyncio
import locale
import calendar
from datetime import datetime, timedelta, time
import pytz
from telethon import TelegramClient
from telegram_utils import authenticate_client
from metrics_calculator import calculate_metrics, fetch_messages_in_period
from google_sheets import get_worksheet
import os
from dotenv import load_dotenv

load_dotenv() 

API_ID = int(os.getenv("API_ID"))  # Преобразуем в int
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_PATH")  # Новый путь
WORKSHEET_NAME = 'Лист1'
CHANNELS_FILE = 'channels.txt'

# Ограничение на число каналов, обрабатываемых параллельно
SEM = asyncio.Semaphore(5)
TZ_MOSCOW = pytz.timezone("Europe/Moscow")

async def process_channel(client, sheet, channel_username,
                          days_ago, start_date, end_date,
                          date_label, month_name):
    try:
    
        await client.connect()
        await client.get_me()
    except ConnectionError as e:
        print(f"Ошибка подключения: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


    async with SEM:
        print(f"\nОбрабатываем канал: {channel_username}")
        try:
            entity = await client.get_entity(channel_username)
            now_msk = datetime.now(TZ_MOSCOW)
            if days_ago is not None:
                period_start = now_msk - timedelta(days=days_ago)
                period_end = now_msk
            else:
                period_start = TZ_MOSCOW.localize(datetime.combine(start_date, time.min))
                period_end = TZ_MOSCOW.localize(datetime.combine(end_date, time.max))
            
            messages = await fetch_messages_in_period(client, entity, period_start, period_end, TZ_MOSCOW)

            metrics = await calculate_metrics(
                entity=entity,
                messages=messages,
                client=client,
                days_ago=days_ago,
                start_date=start_date,
                end_date=end_date,
                tz=TZ_MOSCOW
            )

            row_data = [
                date_label,
                month_name,
                channel_username,
                metrics['subscribers'],
                metrics['total_posts'],
                metrics['total_views'],
                metrics['total_reactions'],
                metrics['total_comments'],
                metrics['total_forwards'],
                round(metrics['avg_reach'], 2),
                round(metrics['er_percent'], 2),
                round(metrics['err_percent'], 2),
                metrics['top_posts'][0]['link'] if metrics.get('top_posts') else 'Нет данных'
            ]

            sheet.append_row(row_data)
            print(f"Данные для канала {channel_username} записаны!")

        except Exception as e:
            print(f"Ошибка обработки канала {channel_username}: {e}")



async def main():
    try:
        locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    except:
        pass

    print("Какой период статистики вы хотите собрать?")
    print("1) За последние N дней (по Москве)")
    print("2) За конкретный диапазон дат (формат YYYY-MM-DD,YYYY-MM-DD; по Москве)")
    print("3) Отчёт за конкретный месяц (YYYY-MM; по Москве)")
    choice = input("Введите 1, 2 или 3: ").strip()

    days_ago = None
    start_date = None
    end_date = None
    date_label = ""
    month_name = ""
    now_msk = datetime.now(TZ_MOSCOW)

    if choice == '1':
        try:
            days_ago = int(input("Сколько дней назад считать? ").strip())
        except ValueError:
            print("Некорректное число!")
            return
        now_str = now_msk.strftime("%d %B %Y %H:%M")
        date_label = f"Последние {days_ago} дней (до {now_str} MSK)"
        month_name = now_msk.strftime("%B %Y")
    elif choice == '2':
        date_range = input("Введите диапазон дат (YYYY-MM-DD,YYYY-MM-DD) по Москве: ").strip()
        try:
            start_str, end_str = date_range.split(',')
            start_date_obj = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date_obj   = datetime.strptime(end_str, "%Y-%m-%d").date()
            start_date_str = datetime.combine(start_date_obj, time.min).strftime("%d %b %Y")
            end_date_str   = datetime.combine(end_date_obj, time.max).strftime("%d %b %Y")
            date_label = f"{start_date_str} – {end_date_str} (MSK)"
            month_name = datetime.combine(start_date_obj, time.min).strftime("%B %Y")
            start_date = start_date_obj
            end_date   = end_date_obj
        except (ValueError, IndexError):
            print("Некорректный формат дат!")
            return
    elif choice == '3':
        month_str = input("Введите месяц в формате YYYY-MM (по Москве): ").strip()
        try:
            year_str, mon_str = month_str.split('-')
            year = int(year_str)
            month = int(mon_str)
            # Начало месяца с учетом часового пояса
            start_date_obj = TZ_MOSCOW.localize(datetime(year, month, 1, 0, 0, 0))
            if (year < now_msk.year) or (year == now_msk.year and month < now_msk.month):
                # Для прошедшего месяца: конец – первый день следующего месяца
                if month == 12:
                    end_date_obj = TZ_MOSCOW.localize(datetime(year + 1, 1, 1, 0, 0, 0))
                else:
                    end_date_obj = TZ_MOSCOW.localize(datetime(year, month + 1, 1, 0, 0, 0))
                date_label = f"Отчёт за {start_date_obj.strftime('%B %Y')} (MSK)"
            else:
                # Для текущего месяца: конец – текущее время
                end_date_obj = now_msk
                date_label = f"Отчёт за {start_date_obj.strftime('%B %Y')} (MSK, по {now_msk.strftime('%d %b %Y %H:%M')})"
            month_name = start_date_obj.strftime("%B %Y")
            start_date = start_date_obj
            end_date = end_date_obj
        except (ValueError, IndexError):
            print("Некорректный формат YYYY-MM!")
            return

    else:
        print("Некорректный выбор!")
        return

    client = TelegramClient('session_name', API_ID, API_HASH)
    await authenticate_client(client, PHONE_NUMBER)

    try:
       sheet = get_worksheet(SPREADSHEET_ID, WORKSHEET_NAME)
    except FileNotFoundError:
        print("Ошибка: Файл credentials.json не найден!")
        return

    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            channels = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Ошибка: Файл {CHANNELS_FILE} не найден!")
        return

    tasks = []
    for channel_username in channels:
        await process_channel(
            client, sheet, channel_username,
            days_ago, start_date, end_date,
            date_label, month_name
        )

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

