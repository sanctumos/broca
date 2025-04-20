from flask import Flask, render_template, request, redirect, url_for
from database import DB_PATH, update_queue_status
import asyncio
import aiosqlite
from collections import namedtuple

app = Flask(__name__)

# Create a namedtuple for queue items
QueueItem = namedtuple('QueueItem', ['queue_id', 'user_id', 'message_id', 'status', 'attempt_count', 'message', 'timestamp', 'username', 'first_name'])

# Sync wrapper for retry_queue_item
def retry_queue_item_sync(queue_id):
    return asyncio.run(update_queue_status(queue_id, 'pending'))

# Sync wrapper for getting all queue items
def get_all_queue_items_sync():
    return asyncio.run(get_all_queue_items())

# Async function to get all queue items
async def get_all_queue_items():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT 
                q.id as queue_id, 
                q.user_id, 
                q.message_id, 
                q.status, 
                q.attempt_count,
                m.message, 
                m.timestamp, 
                COALESCE(u.username, 'Unknown') as username, 
                COALESCE(u.first_name, 'Unknown') as first_name
            FROM queue q
            LEFT JOIN messages m ON q.message_id = m.id
            LEFT JOIN users u ON q.user_id = u.user_id
            ORDER BY q.id DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [QueueItem(*row) for row in rows]

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/queue')
def queue_view():
    queue_items = get_all_queue_items_sync()
    return render_template('partials/queue.html', queue=queue_items)

@app.route('/retry/<int:queue_id>', methods=['POST'])
def retry_queue_item(queue_id):
    retry_queue_item_sync(queue_id)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True) 