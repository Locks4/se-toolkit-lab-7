"""Natural language message handlers using LLM intent routing."""

import sys

from ..services.intent_router import IntentRouter


async def handle_natural_language(message: str, router: IntentRouter) -> str:
    """Handle a natural language message using LLM routing.

    Args:
        message: The user's input message.
        router: The intent router instance.

    Returns:
        The response to send to the user.
    """
    print(f"[DEBUG] Processing message: {message}", file=sys.stderr)
    response = await router.route(message)
    print(f"[DEBUG] Response: {response}", file=sys.stderr)
    return response


def create_inline_keyboard() -> list[list[dict]]:
    """Create inline keyboard with common actions.

    Returns:
        Inline keyboard layout for Telegram.
    """
    return [
        [
            {"text": "📋 Labs", "callback_data": "cmd_labs"},
            {"text": "📊 Scores", "callback_data": "cmd_scores"},
        ],
        [
            {"text": "🏥 Health", "callback_data": "cmd_health"},
            {"text": "❓ Help", "callback_data": "cmd_help"},
        ],
        [
            {"text": "🔄 Sync Data", "callback_data": "cmd_sync"},
        ],
    ]


def get_keyboard_text(keyboard: list[list[dict]]) -> str:
    """Get text representation of inline keyboard.

    Args:
        keyboard: The inline keyboard layout.

    Returns:
        Text description of available quick actions.
    """
    lines = ["\n**Quick Actions:**"]
    for row in keyboard:
        row_text = " | ".join([btn["text"] for btn in row])
        lines.append(f"  {row_text}")
    return "\n".join(lines)
