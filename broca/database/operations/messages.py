"""Message-related database operations (insert, update, history, etc)."""
import os
import json
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
import aiosqlite
from ..models import Message

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sanctum.db")

async def insert_message(
    letta_user_id: int,
    platform_profile_id: int,
    role: str,
    message: str,
    timestamp: Optional[str] = None
) -> int:
    """Insert a new message into the database."""
    now = timestamp or datetime.utcnow().isoformat()
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO messages (
                letta_user_id,
                platform_profile_id,
                role,
                message,
                timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """, (letta_user_id, platform_profile_id, role, message, now))
        await db.commit()
        return cursor.lastrowid

async def get_message_text(message_id: int) -> Optional[Tuple[str, str]]:
    """Get the message text and role for a message ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT role, message 
            FROM messages 
            WHERE id = ?
        """, (message_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return None

async def update_message_with_response(message_id: int, agent_response: str) -> None:
    """Update a message with the agent's response."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE messages 
            SET agent_response = ? 
            WHERE id = ?
        """, (agent_response, message_id))
        await db.commit()

async def get_message_history() -> List[dict]:
    """Get the message history with user details."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT 
                m.id, m.letta_user_id, m.platform_profile_id, m.role,
                m.message, m.agent_response, m.timestamp,
                pp.username, pp.display_name,
                'done' as status
            FROM messages m
            INNER JOIN platform_profiles pp ON m.platform_profile_id = pp.id
            WHERE m.processed = 1 
            AND m.agent_response IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM queue q 
                WHERE q.message_id = m.id 
                AND q.status IN ('pending', 'processing', 'failed')
            )
            ORDER BY m.timestamp DESC
            LIMIT 100
        """) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "letta_user_id": row[1],
                    "platform_profile_id": row[2],
                    "role": row[3],
                    "message": row[4],
                    "agent_response": row[5],
                    "timestamp": row[6],
                    "username": row[7],
                    "display_name": row[8],
                    "status": row[9]
                }
                for row in rows
            ]

async def get_messages(
    letta_user_id: int,
    platform_profile_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get recent messages for a user and platform profile."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT 
                m.id, m.letta_user_id, m.platform_profile_id, 
                m.role, m.message, m.agent_response, m.timestamp
            FROM messages m
            WHERE m.letta_user_id = ? AND m.platform_profile_id = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        """, (letta_user_id, platform_profile_id, limit))
        
        rows = await cursor.fetchall()
        return [{
            "id": row[0],
            "letta_user_id": row[1],
            "platform_profile_id": row[2],
            "role": row[3],
            "message": row[4],
            "agent_response": row[5],
            "timestamp": row[6]
        } for row in rows] 