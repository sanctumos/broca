#!/usr/bin/env python3
import argparse
import asyncio
import sys
from typing import Any

from database.operations import get_all_users, get_user_details, update_letta_user


async def list_users(args) -> None:
    """List all users."""
    users = await get_all_users()
    if args.json:
        print_json(users)
    else:
        print_users(users)


async def get_user(args) -> None:
    """Get a specific user by ID."""
    user_details = await get_user_details(args.id)
    if not user_details:
        print(f"User with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)
        return  # This line should never be reached, but helps with testing

    display_name, username = user_details
    user = {"id": args.id, "display_name": display_name, "username": username}

    if args.json:
        print_json([user])
    else:
        print_users([user])


async def update_user_status(args) -> None:
    """Update a user's status."""
    user = await update_letta_user(args.id, {"is_active": args.status == "active"})
    if not user:
        print(f"User with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)
        return  # This line should never be reached, but helps with testing

    print(f"User {args.id} status updated to {args.status}")


def print_json(data: list[dict[str, Any]]) -> None:
    """Print data in JSON format."""
    import json

    print(json.dumps(data, indent=2))


def print_users(users: list[dict[str, Any]]) -> None:
    """Print users in a human-readable format."""
    if not users:
        print("No users found")
        return

    print("\nUsers:")
    print("-" * 80)
    for user in users:
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Display Name: {user['display_name']}")
        print(f"Status: {'active' if user.get('is_active', True) else 'inactive'}")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Broca2 User Management Tool")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List users command
    subparsers.add_parser("list", help="List all users")

    # Get user command
    get_parser = subparsers.add_parser("get", help="Get user by ID")
    get_parser.add_argument("id", type=int, help="User ID")

    # Update user command
    update_parser = subparsers.add_parser("update", help="Update user status")
    update_parser.add_argument("id", type=int, help="User ID")
    update_parser.add_argument(
        "status", choices=["active", "inactive"], help="New status"
    )

    args = parser.parse_args()

    if args.command == "list":
        asyncio.run(list_users(args))
    elif args.command == "get":
        asyncio.run(get_user(args))
    elif args.command == "update":
        asyncio.run(update_user_status(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
