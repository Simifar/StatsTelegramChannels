import logging
import asyncio
from loader import dp, bot
from handlers import base, stats

# Регистрация роутеров
dp.include_router(base.router)
dp.include_router(stats.router)

logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("Бот запущен.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
