import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'sanctum.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print('Starting migration: Removing conversation_history_limit from letta_users...')

# 1. Create new table without the column (matching actual schema order)
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

# 2. Copy data (exclude conversation_history_limit)
print('Copying data to letta_users_new...')
c.execute('''
    INSERT INTO letta_users_new (id, created_at, last_active, agent_preferences, custom_instructions, is_active, letta_identity_id, letta_block_id)
    SELECT id, created_at, last_active, agent_preferences, custom_instructions, is_active, letta_identity_id, letta_block_id
    FROM letta_users
''')

# 3. Drop old table
print('Dropping old letta_users table...')
c.execute('DROP TABLE letta_users')

# 4. Rename new table
print('Renaming letta_users_new to letta_users...')
c.execute('ALTER TABLE letta_users_new RENAME TO letta_users')

conn.commit()
conn.close()
print('Migration complete!') 