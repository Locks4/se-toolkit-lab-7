"""Configuration loader for the bot.

Loads environment variables from .env.bot.secret (production) or .env.bot.example (development).
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment files.
    
    Returns:
        Dictionary containing all configuration values.
    """
    # Determine the base directory (where this config.py file is located)
    base_dir = Path(__file__).parent
    
    # Try to load .env.bot.secret first (production), fall back to .env.bot.example
    secret_env = base_dir / ".env.bot.secret"
    example_env = base_dir / ".env.bot.example"
    
    if secret_env.exists():
        load_dotenv(secret_env)
    elif example_env.exists():
        load_dotenv(example_env)
    
    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", "http://localhost:42002"),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", "my-secret-api-key"),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", "coder-model"),
    }
