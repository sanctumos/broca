import os
import datetime
import aiosqlite
from typing import Optional, Tuple

# Database file path
DB_PATH = "sanctum.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Create messages table (storing combined conversation logs)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                message TEXT,
                timestamp TEXT,
                processed INTEGER DEFAULT 0,
                gpt_response TEXT
            )
        """)
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_active TEXT,
                message_count INTEGER DEFAULT 0
            )
        """)
        # Create queue table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_id INTEGER,
                status TEXT,  -- 'pending', 'processing', 'done', 'failed'
                attempt_count INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def upsert_user(user_id: int, username: str, first_name: str):
    now = datetime.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE users 
            SET username = ?, first_name = ?, last_active = datetime('now'), message_count = message_count + 1
            WHERE user_id = ?
        """, (username, first_name, user_id))
        if cursor.rowcount == 0:
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, last_active, message_count)
                VALUES (?, ?, ?, datetime('now'), 1)
            """, (user_id, username, first_name))
        await db.commit()

async def insert_message(user_id: int, role: str, message: str, timestamp: Optional[str] = None) -> int:
    if timestamp is None:
        timestamp = datetime.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO messages (user_id, role, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, role, message, timestamp))
        await db.commit()
        return cursor.lastrowid

async def add_to_queue(user_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO queue (user_id, message_id, status, attempt_count)
            VALUES (?, ?, 'pending', 0)
        """, (user_id, message_id))
        await db.commit()

async def get_pending_queue_item() -> Optional[Tuple[int, int, int, int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, user_id, message_id, attempt_count 
            FROM queue 
            WHERE status = 'pending' 
            ORDER BY id ASC 
            LIMIT 1
        """) as cursor:
            return await cursor.fetchone()

async def update_queue_status(queue_id: int, status: str, increment_attempt: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if increment_attempt:
            await db.execute("""
                UPDATE queue 
                SET status = ?, attempt_count = attempt_count + 1 
                WHERE id = ?
            """, (status, queue_id))
        else:
            await db.execute("UPDATE queue SET status = ? WHERE id = ?", (status, queue_id))
        await db.commit()

async def get_message_text(queue_id: int, message_id: int) -> Optional[Tuple[str, str]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT message, timestamp FROM messages WHERE id = ?", (message_id,)) as cur_msg:
            return await cur_msg.fetchone()

async def get_user_details(user_id: int) -> Optional[Tuple[str, str]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT first_name, username FROM users WHERE user_id = ?", (user_id,)) as cur_user:
            return await cur_user.fetchone()

async def get_last_gpt_response(user_id: int) -> Optional[str]:
    """Get the most recent GPT response for the current user."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT gpt_response FROM messages 
            WHERE user_id = ? AND gpt_response IS NOT NULL 
            ORDER BY id DESC LIMIT 1
        """, (user_id,)) as cur_prev_response:
            row = await cur_prev_response.fetchone()
            return row[0] if row else None

async def update_message_with_response(message_id: int, gpt_response: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE messages 
            SET processed = 1, gpt_response = ?
            WHERE id = ?
        """, (gpt_response, message_id))
        await db.commit() 