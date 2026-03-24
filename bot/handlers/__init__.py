"""Handlers package for bot commands.

Handlers are separated from Telegram transport layer for testability.
Each handler receives a command string and returns a text response.
"""

from .base import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_unknown",
]
