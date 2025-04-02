import asyncio
import logging
from bot.loader import bot, dp
from bot.handlers import base, payments

dp.include_router(base.router)
dp.include_router(payments.router)

logging.basicConfig(level=logging.INFO)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())