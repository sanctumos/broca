"""Test script for debugging agent message processing."""
import asyncio
import json
from typing import Dict, Any
from core.agent import AgentClient
from core.message import MessageFormatter

async def test_message_processing(message: str, user_id: int = 424572255, username: str = "@AskDoctorBitcoin") -> None:
    """Test message processing with detailed logging.
    
    Args:
        message: The test message to process
        user_id: The test user ID
        username: The test username
    """
    print("\n=== Starting Message Processing Test ===")
    print(f"Test Message: {message}")
    print(f"User ID: {user_id}")
    print(f"Username: {username}")
    
    # Initialize components
    agent = AgentClient()
    formatter = MessageFormatter()
    
    # Initialize agent
    print("\n🔄 Initializing agent...")
    if not await agent.initialize():
        print("❌ Failed to initialize agent")
        return
    
    # Format message
    print("\n📝 Formatting message...")
    formatted_message = formatter.format_message(
        message=message,
        platform_user_id=user_id,
        username=username
    )
    print(f"Formatted Message: {formatted_message}")
    
    # Process message
    print("\n🤖 Processing message...")
    try:
        response = await agent.process_message(formatted_message)
        print("\n📥 Raw Response:")
        print(json.dumps(response, indent=2, default=str))
        
        if hasattr(response, 'messages') and response.messages:
            print("\n📨 Messages:")
            for msg in response.messages:
                print(f"\nMessage Type: {msg.message_type}")
                print(f"Content: {getattr(msg, 'content', 'No content attribute')}")
                print(f"Reasoning: {getattr(msg, 'reasoning', 'No reasoning attribute')}")
                print(f"Full Message: {msg}")
        else:
            print("\n❌ No messages in response")
            
    except Exception as e:
        print(f"\n❌ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the test script."""
    # Test messages
    test_messages = [
        "Hello, how are you?",
        "What's the weather like?",
        "Tell me a joke",
        "OK< I just implemented a ton of fixes. Working through the list now."
    ]
    
    for msg in test_messages:
        await test_message_processing(msg)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 