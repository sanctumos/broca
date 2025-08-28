#!/usr/bin/env python3
import argparse
import sys
import asyncio
from typing import List, Dict, Any
from database.operations import get_all_queue_items, flush_all_queue_items, delete_queue_item

async def list_queue(args) -> None:
    """List all queue items."""
    items = await get_all_queue_items()
    if args.json:
        print_json(items)
    else:
        print_queue_items(items)

async def flush_queue(args) -> None:
    """Flush all queue items."""
    if args.all:
        success = await flush_all_queue_items("echo")  # Using echo mode as default
        if success:
            print("All queue items flushed successfully")
        else:
            print("Failed to flush queue items", file=sys.stderr)
            sys.exit(1)
    elif args.id:
        # For individual items, we'll mark them as flushed
        success = await delete_queue_item(args.id)
        if success:
            print(f"Queue item {args.id} flushed successfully")
        else:
            print(f"Failed to flush queue item {args.id}", file=sys.stderr)
            sys.exit(1)

async def delete_queue(args) -> None:
    """Delete queue items."""
    if args.all:
        # For all items, we'll delete them
        items = await get_all_queue_items()
        for item in items:
            success = await delete_queue_item(item['id'])
            if not success:
                print(f"Failed to delete queue item {item['id']}", file=sys.stderr)
                sys.exit(1)
        print("All queue items deleted successfully")
    elif args.id:
        success = await delete_queue_item(args.id)
        if success:
            print(f"Queue item {args.id} deleted successfully")
        else:
            print(f"Failed to delete queue item {args.id}", file=sys.stderr)
            sys.exit(1)

def print_json(data: List[Dict[str, Any]]) -> None:
    """Print data in JSON format."""
    import json
    print(json.dumps(data, indent=2))

def print_queue_items(items: List[Dict[str, Any]]) -> None:
    """Print queue items in a human-readable format."""
    if not items:
        print("No items in queue")
        return
    
    print("\nQueue Items:")
    print("-" * 80)
    for item in items:
        print(f"ID: {item['id']}")
        print(f"User: {item['display_name']} (@{item['username']})")
        print(f"Message: {item['message']}")
        print(f"Status: {item['status']}")
        print(f"Attempts: {item['attempts']}")
        print(f"Timestamp: {item['timestamp']}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Broca2 Queue Management Tool')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List queue command
    subparsers.add_parser('list', help='List all queue items')

    # Flush queue commands
    flush_parser = subparsers.add_parser('flush', help='Flush queue items')
    flush_group = flush_parser.add_mutually_exclusive_group(required=True)
    flush_group.add_argument('--all', action='store_true', help='Flush all items')
    flush_group.add_argument('--id', type=int, help='Flush specific item by ID')

    # Delete queue commands
    delete_parser = subparsers.add_parser('delete', help='Delete queue items')
    delete_group = delete_parser.add_mutually_exclusive_group(required=True)
    delete_group.add_argument('--all', action='store_true', help='Delete all items')
    delete_group.add_argument('--id', type=int, help='Delete specific item by ID')

    args = parser.parse_args()

    if args.command == 'list':
        asyncio.run(list_queue(args))
    elif args.command == 'flush':
        asyncio.run(flush_queue(args))
    elif args.command == 'delete':
        asyncio.run(delete_queue(args))
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 