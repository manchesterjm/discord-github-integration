"""
Configuration management for the GitHub-Discord Integration Bot.

This module loads and validates environment variables from the .env file
and provides them to the rest of the application.
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class Config:
    """Configuration class that holds all environment variables."""

    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
    DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

    # Flask Configuration
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required environment variables are set.

        Returns:
            bool: True if all required variables are set, False otherwise.
        """
        required_vars = {
            'DISCORD_BOT_TOKEN': cls.DISCORD_BOT_TOKEN,
            'DISCORD_GUILD_ID': cls.DISCORD_GUILD_ID,
            'DISCORD_CHANNEL_ID': cls.DISCORD_CHANNEL_ID,
            'GITHUB_TOKEN': cls.GITHUB_TOKEN,
            'GITHUB_REPO': cls.GITHUB_REPO,
            'GITHUB_WEBHOOK_SECRET': cls.GITHUB_WEBHOOK_SECRET
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please create a .env file based on .env.example")
            return False

        # Validate GITHUB_REPO format
        if '/' not in cls.GITHUB_REPO:
            logger.error("GITHUB_REPO must be in format 'owner/repository'")
            return False

        logger.info("Configuration validated successfully")
        return True

    @classmethod
    def get_repo_parts(cls) -> tuple[str, str]:
        """
        Split the GitHub repository into owner and repo name.

        Returns:
            tuple[str, str]: A tuple of (owner, repo_name).
        """
        parts = cls.GITHUB_REPO.split('/')
        return parts[0], parts[1]


# Validate configuration on module import
if __name__ != '__main__':
    Config.validate()
