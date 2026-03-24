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
import logging

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health_backend,
    handle_labs_list,
    handle_scores_data,
    handle_unknown,
    handle_health_async,
    handle_labs_async,
    handle_scores_async,
)
from services import LMSClient, LLMClient

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


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


async def run_test_mode(command: str) -> None:
    """Run the bot in test mode.

    Executes a command and prints the response to stdout.

    Args:
        command: The command to execute (e.g., "/start").
    """
    config = load_config()

    cmd, args = parse_command(command)

    # Handle commands with backend integration
    if cmd == "/health":
        response = await handle_health_async(config["LMS_API_URL"], config["LMS_API_KEY"])
    elif cmd == "/labs":
        response = await handle_labs_async(config["LMS_API_URL"], config["LMS_API_KEY"])
    elif cmd == "/scores":
        response = await handle_scores_async(args, config["LMS_API_URL"], config["LMS_API_KEY"])
    elif cmd == "/start":
        response = handle_start(args)
    elif cmd == "/help":
        response = handle_help(args)
    else:
        response = handle_unknown(command)

    print(response)


async def run_production_mode() -> None:
    """Run the bot in production mode with Telegram."""
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )

    config = load_config()

    if not config["BOT_TOKEN"]:
        logger.error("BOT_TOKEN is not set. Please configure .env.bot.secret")
        sys.exit(1)

    logger.info("Starting Telegram bot in production mode...")
    logger.info(f"LMS API URL: {config['LMS_API_URL']}")

    # Create the Application
    application = Application.builder().token(config["BOT_TOKEN"]).build()

    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command from Telegram."""
        response = handle_start()
        await update.message.reply_text(response)

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command from Telegram."""
        response = handle_help()
        await update.message.reply_text(response)

    async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /health command from Telegram."""
        lms_client = LMSClient(config["LMS_API_URL"], config["LMS_API_KEY"])
        is_healthy = await lms_client.health_check()
        backend_status = "✅ Online" if is_healthy else "❌ Offline"
        response = (
            "🏥 **Health Status**\n\n"
            "Bot: ✅ Online\n"
            f"Backend: {backend_status}\n"
            "LLM Service: Checking...\n\n"
            f"{'All systems operational!' if is_healthy else 'Some services are unavailable.'}"
        )
        await update.message.reply_text(response)

    async def labs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /labs command from Telegram."""
        response = handle_labs()
        await update.message.reply_text(response)

    async def scores_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /scores command from Telegram."""
        args = " ".join(context.args) if context.args else ""
        response = handle_scores(args)
        await update.message.reply_text(response)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle non-command messages."""
        text = update.message.text
        response = (
            f"Received your message: {text}\n\n"
            "Use /help to see available commands."
        )
        await update.message.reply_text(response)

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("labs", labs_command))
    application.add_handler(CommandHandler("scores", scores_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    logger.info("Bot is running. Press Ctrl+C to stop.")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)


def run_production_mode_sync() -> None:
    """Synchronous wrapper for production mode."""
    from telegram.ext import Application

    config = load_config()

    if not config["BOT_TOKEN"]:
        logger.error("BOT_TOKEN is not set. Please configure .env.bot.secret")
        sys.exit(1)

    logger.info("Starting Telegram bot in production mode...")
    logger.info(f"LMS API URL: {config['LMS_API_URL']}")

    # Create the Application
    application = Application.builder().token(config["BOT_TOKEN"]).build()

    # Define handlers using sync functions where possible
    async def start_command(update, context):
        await update.message.reply_text(handle_start())

    async def help_command(update, context):
        await update.message.reply_text(handle_help())

    async def health_command(update, context):
        response = await handle_health_async(config["LMS_API_URL"], config["LMS_API_KEY"])
        await update.message.reply_text(response)

    async def labs_command(update, context):
        response = await handle_labs_async(config["LMS_API_URL"], config["LMS_API_KEY"])
        await update.message.reply_text(response)

    async def scores_command(update, context):
        lab_id = " ".join(context.args) if context.args else ""
        if not lab_id:
            await update.message.reply_text("Please specify a lab ID. Example: /scores lab-04")
            return
        response = await handle_scores_async(lab_id, config["LMS_API_URL"], config["LMS_API_KEY"])
        await update.message.reply_text(response)

    async def handle_message(update, context):
        text = update.message.text
        await update.message.reply_text(
            f"Received your message: {text}\n\n"
            "Use /help to see available commands."
        )

    # Add handlers
    from telegram import Update
    from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("labs", labs_command))
    application.add_handler(CommandHandler("scores", scores_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot - run_polling handles its own event loop
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


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
        # run_polling() manages its own event loop, so call it directly
        run_production_mode_sync()


if __name__ == "__main__":
    main()
