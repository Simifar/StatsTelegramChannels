from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

async def authenticate_client(client, phone_number):
    """Авторизация с явным управлением подключением"""
    if not client.is_connected():
        await client.connect()
    
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        try:
            code = input("Введите код: ")
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input("Введите пароль (2FA): ")
            await client.sign_in(password=password)
    return client