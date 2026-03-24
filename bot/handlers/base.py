"""Base command handlers for the bot.

These handlers are pure functions that take command arguments and return responses.
They have no dependency on the Telegram API, making them easy to test.
"""


def handle_start(args: str = "") -> str:
    """Handle /start command.
    
    Args:
        args: Any additional arguments passed with the command.
    
    Returns:
        Welcome message for new users.
    """
    return (
        "👋 Welcome to the Learning Management System Bot!\n\n"
        "I can help you track your academic progress. Here are some commands you can use:\n\n"
        "/labs - View all available labs\n"
        "/scores <lab_id> - View your scores for a specific lab\n"
        "/health - Check bot and backend health status\n"
        "/help - Get help with available commands\n\n"
        "Just type a command or ask me a question!"
    )


def handle_help(args: str = "") -> str:
    """Handle /help command.
    
    Args:
        args: Any additional arguments passed with the command.
    
    Returns:
        Help message with available commands.
    """
    return (
        "📚 **Available Commands**\n\n"
        "/start - Start the bot and see welcome message\n"
        "/labs - List all available labs\n"
        "/scores <lab_id> - Get your scores for a lab (e.g., /scores lab-04)\n"
        "/health - Check system health status\n"
        "/help - Show this help message\n\n"
        "💡 **Tips:**\n"
        "- You can also ask questions in natural language\n"
        "- Use /scores without arguments to see all your scores"
    )


def handle_health(args: str = "") -> str:
    """Handle /health command.
    
    Args:
        args: Any additional arguments passed with the command.
    
    Returns:
        Health status message.
    """
    return (
        "🏥 **Health Status**\n\n"
        "Bot: ✅ Online\n"
        "Backend: Checking...\n"
        "LLM Service: Checking...\n\n"
        "All systems operational!"
    )


def handle_labs(args: str = "") -> str:
    """Handle /labs command.
    
    Args:
        args: Any additional arguments passed with the command.
    
    Returns:
        List of available labs.
    """
    return (
        "📋 **Available Labs**\n\n"
        "Lab 04 - Introduction to Testing\n"
        "Lab 05 - Docker & Containerization\n"
        "Lab 06 - CI/CD Pipeline\n"
        "Lab 07 - Telegram Bot Development\n\n"
        "Use /scores <lab_id> to view your progress on a specific lab."
    )


def handle_scores(args: str = "") -> str:
    """Handle /scores command.
    
    Args:
        args: Lab ID or other arguments (e.g., "lab-04").
    
    Returns:
        Score information for the specified lab.
    """
    if not args:
        return (
            "📊 **Your Scores**\n\n"
            "Lab 04: 85/100 ✅\n"
            "Lab 05: 92/100 ✅\n"
            "Lab 06: 78/100 ✅\n"
            "Lab 07: In Progress 🔄\n\n"
            "Use /scores <lab_id> for detailed breakdown."
        )
    
    lab_id = args.strip()
    return (
        f"📊 **Scores for {lab_id}**\n\n"
        f"Status: Completed ✅\n"
        f"Score: 85/100\n"
        f"Tests Passed: 5/6\n\n"
        f"Keep up the good work!"
    )


def handle_unknown(command: str) -> str:
    """Handle unknown commands.
    
    Args:
        command: The unknown command that was entered.
    
    Returns:
        Message indicating the command is not recognized.
    """
    return (
        f"❓ Unknown command: `{command}`\n\n"
        "Use /help to see available commands."
    )
