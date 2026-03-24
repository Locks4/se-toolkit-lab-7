"""Handlers package for bot commands.

Handlers are separated from Telegram transport layer for testability.
Each handler receives a command string and returns a text response.
"""

from .base import (
    handle_start,
    handle_help,
    handle_health_backend,
    handle_labs_list,
    handle_scores_data,
    handle_unknown,
)
from .backend_handlers import (
    handle_health_async,
    handle_labs_async,
    handle_scores_async,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health_backend",
    "handle_labs_list",
    "handle_scores_data",
    "handle_unknown",
    "handle_health_async",
    "handle_labs_async",
    "handle_scores_async",
]
