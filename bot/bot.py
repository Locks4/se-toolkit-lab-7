#!/usr/bin/env python3
"""Telegram Bot for Learning Management System.

Entry point for the bot with support for:
- Test mode (--test) for local testing without Telegram
- Production mode with Telegram integration

Usage:
    uv run bot.py --test "/start"    # Test mode
    uv run bot.py                    # Production mode (Telegram)
"""

import argparse
import asyncio
import sys

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
)
from services import LMSClient, LLMClient


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command string into command and arguments.
    
    Args:
        text: The full command text (e.g., "/scores lab-04").
    
    Returns:
        Tuple of (command, args).
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0] if parts else ""
    args = parts[1] if len(parts) > 1 else ""
    return command, args


def get_handler(command: str):
    """Get the appropriate handler for a command.
    
    Args:
        command: The command name (e.g., "/start").
    
    Returns:
        The handler function for the command.
    """
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    return handlers.get(command, None)


async def run_test_mode(command: str) -> None:
    """Run the bot in test mode.
    
    Executes a command and prints the response to stdout.
    
    Args:
        command: The command to execute (e.g., "/start").
    """
    config = load_config()
    
    cmd, args = parse_command(command)
    handler = get_handler(cmd)
    
    if handler:
        response = handler(args)
    else:
        response = handle_unknown(command)
    
    # Try to enhance response with backend data if available
    if cmd == "/health":
        lms_client = LMSClient(config["LMS_API_URL"], config["LMS_API_KEY"])
        is_healthy = await lms_client.health_check()
        backend_status = "✅ Online" if is_healthy else "❌ Offline"
        response = (
            "🏥 **Health Status**\n\n"
            f"Bot: ✅ Online\n"
            f"Backend: {backend_status}\n"
            f"LLM Service: Checking...\n\n"
            f"{'All systems operational!' if is_healthy else 'Some services are unavailable.'}"
        )
    
    print(response)


async def run_production_mode() -> None:
    """Run the bot in production mode with Telegram.
    
    Note: This is a placeholder for the full Telegram integration.
    The actual implementation would use python-telegram-bot or similar.
    """
    config = load_config()
    
    if not config["BOT_TOKEN"]:
        print("Error: BOT_TOKEN is not set. Please configure .env.bot.secret")
        sys.exit(1)
    
    print("Starting Telegram bot in production mode...")
    print(f"LMS API URL: {config['LMS_API_URL']}")
    print(f"Bot Token: {'*' * 8}{config['BOT_TOKEN'][-4:] if config['BOT_TOKEN'] else 'NOT SET'}")
    print("\nNote: Full Telegram integration is a placeholder for Task 4.")
    print("For now, use --test mode to test command handlers.")
    
    # Placeholder: In production, this would initialize the Telegram bot
    # and start the event loop for handling updates.
    # Example with python-telegram-bot:
    # from telegram.ext import Application, CommandHandler
    # application = Application.builder().token(config["BOT_TOKEN"]).build()
    # application.add_handler(CommandHandler("start", telegram_handle_start))
    # await application.run_polling()


def main() -> None:
    """Main entry point for the bot."""
    parser = argparse.ArgumentParser(
        description="Telegram Bot for Learning Management System"
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the specified command (e.g., '/start')",
    )
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(run_test_mode(args.test))
        sys.exit(0)
    else:
        asyncio.run(run_production_mode())


if __name__ == "__main__":
    main()
