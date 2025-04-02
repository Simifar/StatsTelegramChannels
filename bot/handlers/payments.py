from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, SuccessfulPayment
from aiogram.filters import Command
from bot.config import PAYMENT_TOKEN
from database.db import get_subscription
from datetime import datetime, timedelta

router = Router()

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    price = 25000
    await message.answer_invoice(
        title="Подписка на Telegram Analyzer",
        description="30 дней доступа к аналитике Telegram-каналов",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[{"label": "Подписка", "amount": price}],
        payload="subscribe-month"
    )

@router.pre_checkout_query(lambda q: True)
async def process_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    now = datetime.now()
    expires = now + timedelta(days=30)

    from database.db import aiosqlite, DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO subscriptions (user_id, status, started_at, expires_at, payment_id)
            VALUES (?, 'active', ?, ?, ?)
        """, (user_id, now.isoformat(), expires.isoformat(), message.successful_payment.provider_payment_charge_id))
        await db.commit()

    await message.answer("✅ Подписка активирована на 30 дней! Спасибо за оплату.")

@router.message(Command("status"))
async def cmd_status(message: Message):
    sub = await get_subscription(message.from_user.id)
    if sub:
        await message.answer(f"✅ Подписка активна до {sub[3]}")
    else:
        await message.answer("🔒 Подписка неактивна. Используйте /subscribe")