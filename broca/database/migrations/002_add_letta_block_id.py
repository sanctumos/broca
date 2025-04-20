"""Migration to add letta_block_id column to letta_users table."""
import os
import aiosqlite
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sanctum.db")

async def migrate():
    """Add letta_block_id column to letta_users table."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Check if column exists
            async with db.execute("PRAGMA table_info(letta_users)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if 'letta_block_id' not in column_names:
                    logger.info("Adding letta_block_id column to letta_users table...")
                    await db.execute("""
                        ALTER TABLE letta_users
                        ADD COLUMN letta_block_id TEXT
                    """)
                    await db.commit()
                    logger.info("Successfully added letta_block_id column")
                else:
                    logger.info("letta_block_id column already exists")
                    
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate()) 