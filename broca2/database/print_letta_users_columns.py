import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'sanctum.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'columns.txt')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

columns = [row[1] for row in c.execute('PRAGMA table_info(letta_users)')]
with open(OUTPUT_PATH, 'w') as f:
    f.write('letta_users columns: ' + ', '.join(columns) + '\n')

conn.close()
print(f'Column names written to {OUTPUT_PATH}') 