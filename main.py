"""
Main entry point for the GitHub-Discord Integration Bot.

This script runs both the Discord bot and the Flask webhook server
concurrently using threading.
"""

import asyncio
import threading
import logging
import signal
import sys

from bot import bot
from webhook_server import run_webhook_server
from config import Config

logger = logging.getLogger(__name__)


def run_flask_in_thread():
    """Run the Flask webhook server in a separate thread."""
    run_webhook_server(bot)


async def main():
    """Main function to run both bot and webhook server."""
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)

    logger.info("Starting GitHub-Discord Integration Bot")

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask_in_thread, daemon=True)
    flask_thread.start()
    logger.info("Webhook server thread started")

    # Start Discord bot
    try:
        await bot.start(Config.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        await bot.close()
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        await bot.close()
        sys.exit(1)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, exiting...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shut down successfully")
