import os
import sys
import asyncio
import datetime
import random
from dotenv import load_dotenv
from telethon import TelegramClient, events
import database

# TODO: Import agent API client here

# Load environment variables
load_dotenv()

# Retrieve and validate credentials from the environment
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")

# TODO: Add agent API credentials here
# agent_api_key = os.getenv("AGENT_API_KEY")
# agent_endpoint = os.getenv("AGENT_ENDPOINT")

# Validate required environment variables
if not all([api_id, api_hash, phone]):
    raise ValueError(
        "Missing required environment variables. Please ensure TELEGRAM_API_ID, "
        "TELEGRAM_API_HASH, and TELEGRAM_PHONE are set in your .env file."
    )

try:
    api_id = int(api_id)
except ValueError:
    raise ValueError("TELEGRAM_API_ID must be a valid integer.")

# Global conversation buffers for streaming message logging
conversation_buffers = {}

# Create but don't start the client
client = TelegramClient('session_name', api_id, api_hash)

# Register the message handler
@client.on(events.NewMessage(incoming=True))
async def handle_private_message(event):
    """Handles new private messages by logging them (streaming mode) and scheduling a flush."""
    sender = await event.get_sender()
    if event.is_private:
        # Sanitize the incoming message text to remove problematic line breaks
        user_message = sanitize_text(event.text)
        sender_first_name = sanitize_text(sender.first_name) if sender.first_name else "Unknown"
        sender_username = sanitize_text(sender.username) if sender.username else "Unknown"
        sender_id = sender.id
        # Use Telegram's message timestamp
        message_date = event.message.date
        print(f"📩 Received message from {sender_first_name} (@{sender_username}, ID: {sender_id}): {user_message}")
        # Upsert user data
        await database.upsert_user(sender_id, sender_username, sender_first_name)
        # Append sanitized message to the conversation buffer
        if sender_id not in conversation_buffers:
            conversation_buffers[sender_id] = {"messages": [], "task": None}
        conversation_buffers[sender_id]["messages"].append((user_message, message_date))
        # Cancel any previously scheduled flush task and schedule a new one
        if conversation_buffers[sender_id]["task"] is not None:
            conversation_buffers[sender_id]["task"].cancel()
        conversation_buffers[sender_id]["task"] = asyncio.create_task(schedule_flush(sender_id))

# --- Utility Function: Sanitize Text ---
def sanitize_text(text):
    """Removes characters outside the BMP and replaces newline/carriage return with spaces."""
    # Replace any newline or carriage return with a space, and remove non-BMP characters.
    sanitized = ''.join(c if (ord(c) <= 0xFFFF and c not in {'\n', '\r'}) else ' ' for c in text)
    # Optionally, collapse multiple spaces into one and trim.
    return ' '.join(sanitized.split())

# --- Streaming Message Logging Functions ---
async def schedule_flush(user_id):
    """Waits for a random delay (3-7 sec) before flushing the user's message buffer.
    If cancelled, it exits gracefully."""
    try:
        delay = random.randint(3, 7)
        print(f"⏱ Scheduling flush for user {user_id} in {delay} seconds...")
        await asyncio.sleep(delay)
        # Only flush if there are still messages in the buffer
        if conversation_buffers.get(user_id, {}).get("messages"):
            await flush_buffer(user_id)
        else:
            print(f"ℹ️ No messages to flush for user {user_id} (buffer already empty).")
    except asyncio.CancelledError:
        print(f"🛑 Flush task for user {user_id} was cancelled.")
        return

async def flush_buffer(user_id):
    """Flushes the conversation buffer for a user: merges messages and queues the combined text safely."""
    buffer = conversation_buffers.get(user_id)
    if not buffer or not buffer["messages"]:
        return
    
    # Use " | " as a safe delimiter instead of newlines
    combined_text = " | ".join(
        f"[{msg_date.astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}] {msg}"
        for msg, msg_date in buffer["messages"]
    )

    first_msg_date = buffer["messages"][0][1].astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    message_id = await database.insert_message(user_id, "user", combined_text, timestamp=first_msg_date)
    await database.add_to_queue(user_id, message_id)

    # Clear the buffer for this user
    conversation_buffers[user_id] = {"messages": [], "task": None}
    print(f"📝 Flushed conversation for user {user_id} safely with {len(buffer['messages'])} messages.")

# --- Queue Processing Function ---
async def process_queue():
    """Background task to process queued messages."""
    while True:
        try:
            # Get the oldest pending message from the queue
            queue_row = await database.get_pending_queue_item()

            if queue_row:
                queue_id, user_id, message_id, attempt_count = queue_row

                # Mark the queue entry as processing and increment attempt_count
                await database.update_queue_status(queue_id, 'processing', increment_attempt=True)

                # Retrieve the message text and timestamp from messages table
                message_data = await database.get_message_text(queue_id, message_id)
                if message_data:
                    message_text, msg_timestamp = message_data
                else:
                    print(f"⚠️ No message found for message_id {message_id} in queue id {queue_id}.")
                    await database.update_queue_status(queue_id, 'done')
                    continue

                # Retrieve user details
                user_data = await database.get_user_details(user_id)
                if user_data:
                    first_name, username = user_data
                else:
                    first_name, username = "Unknown", "Unknown"

                # Build metadata message
                metadata_message = sanitize_text(f"[{msg_timestamp}] Message from {first_name} (@{username}): {message_text}")

                try:
                    print(f"🔄 Processing queued message {queue_id} for user {user_id}...")
                    
                    # TODO: Replace this section with agent API call
                    # This is where we'll send the message to the agent and get the response
                    # Example:
                    # agent_response = await agent_client.process_message(metadata_message)
                    agent_response = "TODO: Implement agent API response"
                    
                    # Use Telegram's typing indicator while processing
                    async with client.action(user_id, action='typing'):
                        # TODO: Process the agent's response
                        # This might include additional processing or formatting
                        await client.send_message(user_id, agent_response)

                    # Update message status
                    await database.update_message_with_response(message_id, agent_response)
                    await database.update_queue_status(queue_id, 'done')

                except Exception as e:
                    print(f"❌ Error processing message: {str(e)}")
                    await database.update_queue_status(queue_id, 'failed')

            await asyncio.sleep(1)  # Prevent tight loop

        except Exception as e:
            print(f"❌ Queue processing error: {str(e)}")
            await asyncio.sleep(5)  # Back off on error

if __name__ == '__main__':
    # For direct script execution, use a simple runner
    asyncio.run(database.init_db())
    with client:
        client.loop.run_until_complete(client.start(phone=phone))
        print("🤖 Listening for DMs...")
        client.loop.run_until_complete(client.run_until_disconnected())
