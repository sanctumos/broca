import asyncio
from sanctum_dashboard import app
import telegram_chatgpt
# TODO: Import agent API client here
from threading import Thread

def run_flask():
    app.run(debug=True, use_reloader=False, port=5000)

async def run_bot():
    # Initialize the SQLite database
    await telegram_chatgpt.database.init_db()

    # TODO: Initialize agent API client here
    
    # Start the queue processing task
    asyncio.create_task(telegram_chatgpt.process_queue())

    # Start the Telegram client
    print("📱 Starting Telegram client...")
    await telegram_chatgpt.client.start(phone=telegram_chatgpt.phone)
    print("🤖 Listening for DMs...")
    await telegram_chatgpt.client.run_until_disconnected()

if __name__ == '__main__':
    try:
        # TODO: Initialize agent API connection here
        print("🔄 Initializing agent API connection...")
        
        # Start Flask in a separate thread
        print("🌐 Starting dashboard server...")
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        # Run the Telegram bot in the main thread with the event loop
        print("🤖 Starting Telegram bot...")
        with telegram_chatgpt.client:
            asyncio.get_event_loop().run_until_complete(run_bot())

    except KeyboardInterrupt:
        print("\n⚠️ Shutting down...")
        # TODO: Clean up agent API connection here
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise 