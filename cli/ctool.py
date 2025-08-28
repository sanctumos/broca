#!/usr/bin/env python3
import argparse
import sys
import asyncio
from typing import List, Dict, Any
from database.operations import get_message_history

async def list_conversations(args) -> None:
    """List recent conversations."""
    conversations = await get_message_history()
    if args.json:
        print_json(conversations)
    else:
        print_conversations(conversations)

async def get_conversation(args) -> None:
    """Get conversation history for a specific user."""
    conversations = await get_message_history()
    # Filter conversations for the specific user
    user_conversations = [
        conv for conv in conversations 
        if conv['letta_user_id'] == args.user_id and conv['platform_profile_id'] == args.platform_id
    ][:args.limit]
    
    if args.json:
        print_json(user_conversations)
    else:
        print_conversations(user_conversations)

def print_json(data: List[Dict[str, Any]]) -> None:
    """Print data in JSON format."""
    import json
    print(json.dumps(data, indent=2))

def print_conversations(conversations: List[Dict[str, Any]]) -> None:
    """Print conversations in a human-readable format."""
    if not conversations:
        print("No conversations found")
        return
    
    print("\nRecent Conversations:")
    print("-" * 80)
    for conv in conversations:
        print(f"User: {conv['display_name']} (@{conv['username']})")
        print(f"Message: {conv['message']}")
        print(f"Response: {conv['agent_response']}")
        print(f"Timestamp: {conv['timestamp']}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Broca2 Conversation Management Tool')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List conversations command
    subparsers.add_parser('list', help='List recent conversations')

    # Get conversation command
    get_parser = subparsers.add_parser('get', help='Get conversation history for a user')
    get_parser.add_argument('user_id', type=int, help='Letta user ID')
    get_parser.add_argument('platform_id', type=int, help='Platform profile ID')
    get_parser.add_argument('--limit', type=int, default=10, help='Number of messages to retrieve (default: 10)')

    args = parser.parse_args()

    if args.command == 'list':
        asyncio.run(list_conversations(args))
    elif args.command == 'get':
        asyncio.run(get_conversation(args))
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 