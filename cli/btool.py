# -*- coding: utf-8 -*-
"""
Bot management CLI tool.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""Bot management CLI tool."""
import argparse
import json
import logging
import os
from typing import List, Optional, Dict, Union
from pathlib import Path

logger = logging.getLogger(__name__)

def get_ignore_list_path() -> Path:
    """Get the path to the ignore list file."""
    return Path("telegram_ignore_list.json")

def load_ignore_list() -> Dict[str, Dict[str, str]]:
    """Load the ignore list from file.
    
    Returns:
        Dict[str, Dict[str, str]]: Dictionary of ignored bots with their IDs and usernames
    """
    path = get_ignore_list_path()
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("Failed to parse ignore list file")
        return {}

def save_ignore_list(bots: Dict[str, Dict[str, str]]) -> None:
    """Save the ignore list to file.
    
    Args:
        bots: Dictionary of ignored bots with their IDs and usernames
    """
    path = get_ignore_list_path()
    with open(path, 'w') as f:
        json.dump(bots, f, indent=2)

def add_bot(identifier: str, bot_id: Optional[str] = None) -> None:
    """Add a bot to the ignore list.
    
    Args:
        identifier: The bot username (with or without @) or ID to add
        bot_id: Optional numeric ID for the bot
    """
    ignored = load_ignore_list()
    
    # Handle username input
    if identifier.startswith('@'):
        identifier = identifier[1:]  # Remove @ if present
    
    # Check if bot is already in list by username
    for existing_id, data in ignored.items():
        if data.get("username") == identifier:
            if bot_id and bot_id != existing_id:
                # Update ID if provided and different
                del ignored[existing_id]
                ignored[bot_id] = {"username": identifier}
                save_ignore_list(ignored)
                print(f"Updated ID for @{identifier} to {bot_id}")
            else:
                print(f"Bot @{identifier} is already in ignore list")
            return
    
    # Check if bot is already in list by ID
    if bot_id and bot_id in ignored:
        if ignored[bot_id].get("username") != identifier:
            ignored[bot_id]["username"] = identifier
            save_ignore_list(ignored)
            print(f"Updated username for bot {bot_id} to @{identifier}")
        else:
            print(f"Bot {bot_id} is already in ignore list")
        return
    
    # Add new bot
    if bot_id:
        ignored[bot_id] = {"username": identifier}
    else:
        # Use username as temporary key if no ID provided
        ignored[identifier] = {"username": identifier}
    
    save_ignore_list(ignored)
    print(f"Added bot @{identifier}" + (f" (ID: {bot_id})" if bot_id else " (ID pending)") + " to ignore list")

def remove_bot(identifier: str) -> None:
    """Remove a bot from the ignore list.
    
    Args:
        identifier: The bot ID or username to remove
    """
    ignored = load_ignore_list()
    
    # Check if identifier is a username
    if identifier.startswith('@'):
        identifier = identifier[1:]  # Remove @ if present
        # Find bot by username
        for bot_id, data in ignored.items():
            if data.get("username") == identifier:
                del ignored[bot_id]
                save_ignore_list(ignored)
                print(f"Removed bot @{identifier} from ignore list")
                return
        print(f"Bot with username @{identifier} not found in ignore list")
    else:
        # Remove by ID
        if identifier in ignored:
            del ignored[identifier]
            save_ignore_list(ignored)
            print(f"Removed bot {identifier} from ignore list")
        else:
            print(f"Bot {identifier} is not in ignore list")

def list_bots() -> None:
    """List all ignored bots."""
    ignored = load_ignore_list()
    if not ignored:
        print("No bots in ignore list")
        return
    
    print("Ignored bots:")
    for bot_id, data in ignored.items():
        username = data.get("username")
        if username == bot_id:  # This is a temporary entry with no ID
            print(f"- @{username} (ID pending)")
        else:
            print(f"- {bot_id} (@{username})")

def main():
    parser = argparse.ArgumentParser(description='Bot Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add bot command
    add_parser = subparsers.add_parser('add', help='Add a bot to ignore list')
    add_parser.add_argument('identifier', help='Bot username (with or without @) or ID to add')
    add_parser.add_argument('--id', help='Optional numeric ID for the bot')

    # Remove bot command
    remove_parser = subparsers.add_parser('remove', help='Remove a bot from ignore list')
    remove_parser.add_argument('identifier', help='Bot ID or username to remove')

    # List bots command
    subparsers.add_parser('list', help='List ignored bots')

    args = parser.parse_args()

    if args.command == 'add':
        add_bot(args.identifier, args.id)
    elif args.command == 'remove':
        remove_bot(args.identifier)
    elif args.command == 'list':
        list_bots()
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 