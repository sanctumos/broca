import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'sanctum.db')

try:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print('Checking current letta_users columns:')
    before_cols = [row[1] for row in c.execute('PRAGMA table_info(letta_users)')]
    print('Before:', before_cols)

    # Drop leftover migration table if exists
    c.execute('DROP TABLE IF EXISTS letta_users_new')
    conn.commit()

    # Create new table with correct columns (excluding conversation_history_limit)
    table_sql = '''
    CREATE TABLE letta_users_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT,
        agent_preferences TEXT,
        custom_instructions TEXT,
        is_active INTEGER DEFAULT 1,
        letta_identity_id TEXT,
        letta_block_id TEXT
    )
    '''
    print('Creating letta_users_new table...')
    c.execute(table_sql)

    # Copy data (exclude conversation_history_limit)
    print('Copying data to letta_users_new...')
    c.execute('''
        INSERT INTO letta_users_new (id, created_at, last_active, agent_preferences, custom_instructions, is_active, letta_identity_id, letta_block_id)
        SELECT id, created_at, last_active, agent_preferences, custom_instructions, is_active, letta_identity_id, letta_block_id
        FROM letta_users
    ''')

    # Drop old table
    print('Dropping old letta_users table...')
    c.execute('DROP TABLE letta_users')

    # Rename new table
    print('Renaming letta_users_new to letta_users...')
    c.execute('ALTER TABLE letta_users_new RENAME TO letta_users')

    conn.commit()

    # Print columns after migration
    after_cols = [row[1] for row in c.execute('PRAGMA table_info(letta_users)')]
    print('After:', after_cols)

    conn.close()
    print('Migration complete!')
except Exception as e:
    print('Migration failed:', e)
    sys.exit(1) 