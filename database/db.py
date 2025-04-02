import aiosqlite
from datetime import datetime, timedelta

DB_PATH = "storage/database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TEXT,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER,
                status TEXT,
                started_at TEXT,
                expires_at TEXT,
                payment_id TEXT
            )
        """)
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return await cursor.fetchone()

async def create_user(user_id: int, username: str, full_name: str, is_admin: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (id, username, full_name, created_at, is_admin)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, full_name, datetime.now().isoformat(), int(is_admin)))
        await db.commit()

async def create_trial_subscription(user_id: int):
    now = datetime.now()
    expires = now + timedelta(days=3)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO subscriptions (user_id, status, started_at, expires_at, payment_id)
            VALUES (?, 'trial', ?, ?, NULL)
        """, (user_id, now.isoformat(), expires.isoformat()))
        await db.commit()

async def get_subscription(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT * FROM subscriptions WHERE user_id = ? ORDER BY expires_at DESC LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        expires = datetime.fromisoformat(row[3])
        if expires < datetime.now():
            return None
        return row