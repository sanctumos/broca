import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'sanctum.db.bak')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

columns = [row for row in c.execute('PRAGMA table_info(letta_users)')]
print('letta_users columns:')
for col in columns:
    print(col)

schema = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='letta_users'").fetchone()
print('\nletta_users CREATE TABLE statement:')
print(schema[0] if schema else 'Not found')

conn.close() 