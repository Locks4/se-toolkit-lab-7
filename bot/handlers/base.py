"""Base command handlers for the bot.

These handlers are pure functions that take command arguments and return responses.
They have no dependency on the Telegram API, making them easy to test.

For backend-integrated handlers, use the async versions in backend_handlers.py.
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


def handle_health_backend(backend_status: str, error_detail: str = "") -> str:
    """Handle /health command with backend status.

    Args:
        backend_status: Status of the backend (e.g., "✅ Online", "❌ Offline").
        error_detail: Optional error detail if backend is down.

    Returns:
        Health status message.
    """
    base_response = (
        "🏥 **Health Status**\n\n"
        "Bot: ✅ Online\n"
        f"Backend: {backend_status}\n"
    )
    
    if error_detail:
        base_response += f"\n⚠️ {error_detail}\n"
    
    if "✅" in backend_status:
        base_response += "\nAll systems operational!"
    else:
        base_response += "\nSome services are unavailable."
    
    return base_response


def handle_labs_list(labs: list[dict]) -> str:
    """Handle /labs command with real lab data.

    Args:
        labs: List of labs from the backend.

    Returns:
        Formatted list of labs.
    """
    if not labs:
        return "📋 **Available Labs**\n\nNo labs available at the moment."
    
    lab_lines = []
    for i, lab in enumerate(labs, 1):
        lab_name = lab.get("name", f"Lab {i}")
        lab_id = lab.get("id", f"lab-{i}")
        lab_lines.append(f"• {lab_name} (`{lab_id}`)")
    
    return "📋 **Available Labs**\n\n" + "\n".join(lab_lines) + "\n\nUse /scores <lab_id> to view your progress."


def handle_scores_data(lab_id: str, scores: dict | list) -> str:
    """Handle /scores command with real score data.

    Args:
        lab_id: The lab identifier.
        scores: Score data from the backend (dict or list).

    Returns:
        Formatted score information.
    """
    if not scores:
        return f"📊 **Scores for {lab_id}**\n\nNo score data available for this lab."
    
    # Handle list of task scores
    if isinstance(scores, list):
        lines = [f"📊 **Scores for {lab_id}**\n"]
        for item in scores:
            task_name = item.get("task_name", item.get("name", "Unknown"))
            pass_rate = item.get("pass_rate", item.get("score", 0))
            lines.append(f"• {task_name}: {pass_rate}%")
        return "\n".join(lines)
    
    # Handle dict format
    if isinstance(scores, dict):
        lines = [f"📊 **Scores for {lab_id}**\n"]
        for task_name, score in scores.items():
            if isinstance(score, (int, float)):
                lines.append(f"• {task_name}: {score}%")
        if len(lines) > 1:
            return "\n".join(lines)
        return f"📊 **Scores for {lab_id}**\n\nScore: {scores.get('score', 'N/A')}"
    
    return f"📊 **Scores for {lab_id}**\n\nData received but could not be parsed."


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
