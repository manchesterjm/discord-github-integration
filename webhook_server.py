"""
Flask webhook server for receiving GitHub webhook events.

This server receives webhook events from GitHub, validates them,
and sends formatted notifications to Discord via the bot.
"""

from flask import Flask, request, jsonify
import hmac
import hashlib
import logging
import asyncio
import discord

from config import Config
from utils import MessageFormatter

# Set up logging
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store reference to Discord bot (will be set when server starts)
discord_bot = None


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify that the webhook payload came from GitHub.

    Args:
        payload: Raw request body as bytes
        signature: X-Hub-Signature-256 header from GitHub

    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not signature:
        logger.warning("No signature provided in webhook request")
        return False

    # GitHub sends signature as "sha256=<hash>"
    if not signature.startswith('sha256='):
        logger.warning("Invalid signature format")
        return False

    # Extract the hash from the signature
    received_hash = signature.split('=')[1]

    # Compute expected hash
    secret = Config.GITHUB_WEBHOOK_SECRET.encode('utf-8')
    expected_hash = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    # Compare hashes (use compare_digest to prevent timing attacks)
    is_valid = hmac.compare_digest(expected_hash, received_hash)

    if not is_valid:
        logger.warning("Webhook signature validation failed")

    return is_valid


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Handle incoming GitHub webhook events.

    Returns:
        JSON response with status
    """
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        logger.error("Webhook signature verification failed")
        return jsonify({'error': 'Invalid signature'}), 401

    # Get event type
    event_type = request.headers.get('X-GitHub-Event')
    if not event_type:
        logger.error("No event type in webhook request")
        return jsonify({'error': 'No event type'}), 400

    # Get payload
    payload = request.json
    if not payload:
        logger.error("No payload in webhook request")
        return jsonify({'error': 'No payload'}), 400

    logger.info(f"Received {event_type} event from GitHub")

    # Process the event
    try:
        embed = None

        if event_type == 'push':
            embed = handle_push_event(payload)

        elif event_type == 'pull_request':
            embed = handle_pull_request_event(payload)

        elif event_type == 'pull_request_review':
            embed = handle_review_event(payload)

        elif event_type == 'pull_request_review_comment':
            embed = handle_review_comment_event(payload)

        elif event_type == 'issues':
            embed = handle_issue_event(payload)

        elif event_type == 'create':
            embed = handle_create_event(payload)

        elif event_type == 'delete':
            embed = handle_delete_event(payload)

        else:
            logger.info(f"Unhandled event type: {event_type}")

        # Send notification to Discord if we created an embed
        if embed and discord_bot:
            asyncio.run_coroutine_threadsafe(
                discord_bot.send_notification(embed),
                discord_bot.loop
            )

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


def handle_push_event(payload: dict) -> discord.Embed:
    """
    Handle push events (new commits).

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    # Skip if no commits (e.g., branch creation)
    if not payload.get('commits'):
        return None

    embed = MessageFormatter.format_commit_notification(payload)
    logger.info(f"Processed push event for {payload['ref']}")
    return embed


def handle_pull_request_event(payload: dict) -> discord.Embed:
    """
    Handle pull request events (opened, closed, merged, reopened).

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    action = payload['action']

    # Only process certain actions
    if action not in ['opened', 'closed', 'reopened']:
        return None

    embed = MessageFormatter.format_pull_request_notification(payload)
    logger.info(f"Processed pull_request event: {action}")
    return embed


def handle_review_event(payload: dict) -> discord.Embed:
    """
    Handle pull request review events.

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    action = payload['action']

    # Only process submitted reviews
    if action != 'submitted':
        return None

    embed = MessageFormatter.format_review_notification(payload)
    logger.info(f"Processed pull_request_review event")
    return embed


def handle_review_comment_event(payload: dict) -> discord.Embed:
    """
    Handle pull request review comment events.

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    action = payload['action']

    # Only process created comments
    if action != 'created':
        return None

    # For now, we'll skip individual review comments to avoid spam
    # You can uncomment below to enable review comment notifications
    # comment = payload['comment']
    # pr = payload['pull_request']
    # ...
    # return embed

    logger.info(f"Skipped pull_request_review_comment event (to avoid spam)")
    return None


def handle_issue_event(payload: dict) -> discord.Embed:
    """
    Handle issue events (opened, closed, etc.).

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    action = payload['action']

    # Only process certain actions
    if action not in ['opened', 'closed', 'reopened']:
        return None

    embed = MessageFormatter.format_issue_notification(payload)
    logger.info(f"Processed issues event: {action}")
    return embed


def handle_create_event(payload: dict) -> discord.Embed:
    """
    Handle create events (branch or tag created).

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    ref_type = payload.get('ref_type')

    # Only process branch creation
    if ref_type != 'branch':
        return None

    embed = MessageFormatter.format_branch_notification(payload, deleted=False)
    logger.info(f"Processed create event: {ref_type}")
    return embed


def handle_delete_event(payload: dict) -> discord.Embed:
    """
    Handle delete events (branch or tag deleted).

    Args:
        payload: GitHub webhook payload

    Returns:
        Discord embed for the event
    """
    ref_type = payload.get('ref_type')

    # Only process branch deletion
    if ref_type != 'branch':
        return None

    embed = MessageFormatter.format_branch_notification(payload, deleted=True)
    logger.info(f"Processed delete event: {ref_type}")
    return embed


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response indicating server is running
    """
    return jsonify({'status': 'ok', 'message': 'Webhook server is running'}), 200


def run_webhook_server(bot):
    """
    Run the Flask webhook server.

    Args:
        bot: Discord bot instance to send notifications through
    """
    global discord_bot
    discord_bot = bot

    logger.info(f"Starting webhook server on port {Config.FLASK_PORT}")
    app.run(host='0.0.0.0', port=Config.FLASK_PORT, debug=False)


if __name__ == '__main__':
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        exit(1)

    # Run server standalone (without bot)
    logger.warning("Running webhook server without Discord bot connection")
    app.run(host='0.0.0.0', port=Config.FLASK_PORT, debug=True)
