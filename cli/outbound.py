#!/usr/bin/env python3
"""CLI for headless outbound messaging (SMCP / operators)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from dotenv import load_dotenv

from common.logging import setup_logging
from runtime.core.outbound import send_outbound_message

load_dotenv()
setup_logging(use_emojis=False)


async def cmd_send(args: argparse.Namespace) -> None:
    dry = str(args.dry_run).lower() == "yes"
    result = await send_outbound_message(
        letta_user_id=int(args.letta_user_id),
        platform=str(args.platform),
        message=str(args.message),
        dry_run=dry,
        idempotency_key=args.idempotency_key,
    )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Broca outbound messaging (requires ENABLE_OUTBOUND_TOOL=true unless dry-run validation only)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON (default is also JSON)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("send", help="Send an outbound message to a user on a platform")
    p.add_argument("--letta-user-id", type=int, required=True)
    p.add_argument("--platform", required=True, help="e.g. telegram")
    p.add_argument("--message", required=True)
    p.add_argument(
        "--dry-run",
        choices=("yes", "no"),
        default="no",
        help="yes = resolve profile only, no DB insert / no send",
    )
    p.add_argument("--idempotency-key", default=None, dest="idempotency_key")

    args = parser.parse_args()
    if args.command == "send":
        asyncio.run(cmd_send(args))


if __name__ == "__main__":
    main()
