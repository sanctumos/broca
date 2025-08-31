#!/usr/bin/env python3
import argparse
import sys
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Get the path to the settings file (relative to broca2 directory)
SETTINGS_PATH = Path(os.path.dirname(os.path.dirname(__file__))) / "settings.json"

def load_settings() -> Dict[str, Any]:
    """Load settings from settings.json"""
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            # logger.info(f"Loaded settings from {SETTINGS_PATH.absolute()}")
            return settings
    # Default settings
    default_settings = {
        "debug_mode": False,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "live"
    }
    # logger.info(f"Created default settings as {SETTINGS_PATH.absolute()} does not exist")
    return default_settings

def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to settings.json"""
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)
    # logger.info(f"Saved settings to {SETTINGS_PATH.absolute()}")
    # logger.info(f"Settings content: {json.dumps(settings, indent=2)}")

def print_output(data: Any, json_output: bool) -> None:
    """Print output in either human-readable or JSON format"""
    if json_output:
        print(json.dumps(data, indent=2))
    else:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, bool):
                    value = 'enabled' if value else 'disabled'
                print(f"{key}: {value}")
        else:
            print(data)

def get_settings(args) -> None:
    """Display current settings"""
    settings = load_settings()
    if args.json:
        print_output(settings, True)
    else:
        print("\nCurrent Settings:")
        print_output(settings, False)
        print()

def set_message_mode(args) -> None:
    """Set message mode"""
    valid_modes = ['echo', 'listen', 'live']
    if args.mode not in valid_modes:
        error_msg = f"Error: Invalid message mode. Must be one of: {', '.join(valid_modes)}"
        print_output({"error": error_msg}, args.json)
        sys.exit(1)
    
    settings = load_settings()
    # logger.info(f"Current message mode: {settings.get('message_mode', 'not set')}")
    settings['message_mode'] = args.mode
    save_settings(settings)
    # logger.info(f"Message mode set to: {args.mode}")
    print_output({"message_mode": args.mode}, args.json)

def set_debug_mode(args) -> None:
    """Set debug mode"""
    settings = load_settings()
    # logger.info(f"Current debug mode: {settings.get('debug_mode', 'not set')}")
    settings['debug_mode'] = args.enable
    save_settings(settings)
    # logger.info(f"Debug mode set to: {args.enable}")
    print_output({"debug_mode": args.enable}, args.json)

def set_queue_refresh(args) -> None:
    """Set queue refresh interval"""
    if args.seconds < 1:
        error_msg = "Error: Queue refresh must be at least 1 second"
        print_output({"error": error_msg}, args.json)
        sys.exit(1)
    
    settings = load_settings()
    # logger.info(f"Current queue refresh: {settings.get('queue_refresh', 'not set')}")
    settings['queue_refresh'] = args.seconds
    save_settings(settings)
    # logger.info(f"Queue refresh set to: {args.seconds}")
    print_output({"queue_refresh": args.seconds}, args.json)

def set_max_retries(args) -> None:
    """Set maximum retries"""
    if args.retries < 0:
        error_msg = "Error: Max retries must be non-negative"
        print_output({"error": error_msg}, args.json)
        sys.exit(1)
    
    settings = load_settings()
    # logger.info(f"Current max retries: {settings.get('max_retries', 'not set')}")
    settings['max_retries'] = args.retries
    save_settings(settings)
    # logger.info(f"Max retries set to: {args.retries}")
            print_output({"max_retries": args.retries}, args.json)

def reload_settings(args) -> None:
    """Force reload of settings by touching the settings file"""
    try:
        import os
        import time
        
        # Touch the settings file to trigger reload
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            current_time = time.time()
            os.utime(settings_file, (current_time, current_time))
            print_output({"status": "Settings file touched, reload should occur within 1 second"}, args.json)
        else:
            print_output({"error": "Settings file not found"}, args.json)
            sys.exit(1)
    except Exception as e:
        print_output({"error": f"Failed to reload settings: {str(e)}"}, args.json)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Broca2 Settings Management Tool')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Get settings command
    subparsers.add_parser('get', help='Display current settings')

    # Message mode commands
    mode_parser = subparsers.add_parser('mode', help='Message mode management')
    mode_parser.add_argument('mode', choices=['echo', 'listen', 'live'], 
                           help='Set message mode')

    # Debug mode commands
    debug_parser = subparsers.add_parser('debug', help='Debug mode management')
    debug_group = debug_parser.add_mutually_exclusive_group(required=True)
    debug_group.add_argument('--enable', action='store_true', help='Enable debug mode')
    debug_group.add_argument('--disable', action='store_false', dest='enable', 
                           help='Disable debug mode')

    # Queue refresh commands
    refresh_parser = subparsers.add_parser('refresh', help='Queue refresh management')
    refresh_parser.add_argument('seconds', type=int, help='Queue refresh interval in seconds')

    # Max retries commands
    retries_parser = subparsers.add_parser('retries', help='Maximum retries management')
    retries_parser.add_argument('retries', type=int, help='Maximum number of retries')

    # Reload settings command
    subparsers.add_parser('reload', help='Force reload of settings file')

    args = parser.parse_args()

    if args.command == 'get':
        get_settings(args)
    elif args.command == 'mode':
        set_message_mode(args)
    elif args.command == 'debug':
        set_debug_mode(args)
    elif args.command == 'refresh':
        set_queue_refresh(args)
    elif args.command == 'retries':
        set_max_retries(args)
    elif args.command == 'reload':
        reload_settings(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
