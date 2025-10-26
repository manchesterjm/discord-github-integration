"""
Discord Bot for GitHub Integration.

This bot provides slash commands to interact with GitHub repositories
and receive real-time notifications about repository activity.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
from typing import Optional

from config import Config
from utils import GitHubAPI, MessageFormatter

# Set up logging
logger = logging.getLogger(__name__)


class GitHubBot(commands.Bot):
    """Custom Discord bot class for GitHub integration."""

    def __init__(self):
        """Initialize the bot with required intents and configuration."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True

        super().__init__(command_prefix='!', intents=intents)

        # Initialize GitHub API client
        self.github = GitHubAPI(Config.GITHUB_TOKEN, Config.GITHUB_REPO)
        self.notification_channel_id = int(Config.DISCORD_CHANNEL_ID)
        self.notification_channel: Optional[discord.TextChannel] = None

    async def setup_hook(self):
        """Set up the bot before it starts running."""
        logger.info("Setting up bot...")

        # Sync commands with Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")

        # Get the notification channel
        self.notification_channel = self.get_channel(self.notification_channel_id)
        if self.notification_channel:
            logger.info(f"Notification channel set to: {self.notification_channel.name}")
        else:
            logger.warning(f"Could not find notification channel with ID: {self.notification_channel_id}")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{Config.GITHUB_REPO}"
            )
        )

    async def send_notification(self, embed: discord.Embed):
        """
        Send a notification to the configured notification channel.

        Args:
            embed: Discord embed to send
        """
        if self.notification_channel:
            try:
                await self.notification_channel.send(embed=embed)
                logger.info("Notification sent successfully")
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
        else:
            logger.warning("Notification channel not set")


# Initialize the bot
bot = GitHubBot()


@bot.tree.command(name="prs", description="List all open pull requests")
async def list_prs(interaction: discord.Interaction):
    """
    List all open pull requests with their status.

    Args:
        interaction: Discord interaction object
    """
    await interaction.response.defer()

    try:
        prs = bot.github.get_open_pull_requests()
        embed = MessageFormatter.format_pr_list(prs)
        await interaction.followup.send(embed=embed)
        logger.info(f"User {interaction.user} requested PR list")
    except Exception as e:
        logger.error(f"Error in /prs command: {e}")
        await interaction.followup.send(
            "An error occurred while fetching pull requests. Please try again later.",
            ephemeral=True
        )


@bot.tree.command(name="pr", description="Get detailed information about a specific pull request")
@app_commands.describe(number="Pull request number")
async def get_pr(interaction: discord.Interaction, number: int):
    """
    Get detailed information about a specific pull request.

    Args:
        interaction: Discord interaction object
        number: Pull request number
    """
    await interaction.response.defer()

    try:
        pr = bot.github.get_pull_request(number)
        if pr:
            embed = MessageFormatter.format_pr_detail(pr)
            await interaction.followup.send(embed=embed)
            logger.info(f"User {interaction.user} requested PR #{number}")
        else:
            await interaction.followup.send(
                f"Pull request #{number} not found.",
                ephemeral=True
            )
    except Exception as e:
        logger.error(f"Error in /pr command: {e}")
        await interaction.followup.send(
            "An error occurred while fetching the pull request. Please try again later.",
            ephemeral=True
        )


@bot.tree.command(name="commits", description="Show recent commits on a branch")
@app_commands.describe(branch="Branch name (default: main)")
async def get_commits(interaction: discord.Interaction, branch: str = "main"):
    """
    Show recent commits on a specified branch.

    Args:
        interaction: Discord interaction object
        branch: Branch name (default: main)
    """
    await interaction.response.defer()

    try:
        commits = bot.github.get_commits(branch=branch, limit=10)
        if commits:
            embed = MessageFormatter.format_commit_list(commits, branch)
            await interaction.followup.send(embed=embed)
            logger.info(f"User {interaction.user} requested commits for branch '{branch}'")
        else:
            await interaction.followup.send(
                f"No commits found for branch `{branch}` or branch does not exist.",
                ephemeral=True
            )
    except Exception as e:
        logger.error(f"Error in /commits command: {e}")
        await interaction.followup.send(
            f"An error occurred while fetching commits for branch `{branch}`. Please check the branch name and try again.",
            ephemeral=True
        )


@bot.tree.command(name="branches", description="List all branches in the repository")
async def list_branches(interaction: discord.Interaction):
    """
    List all branches in the repository.

    Args:
        interaction: Discord interaction object
    """
    await interaction.response.defer()

    try:
        branches = bot.github.get_branches()
        embed = MessageFormatter.format_branch_list(branches)
        await interaction.followup.send(embed=embed)
        logger.info(f"User {interaction.user} requested branch list")
    except Exception as e:
        logger.error(f"Error in /branches command: {e}")
        await interaction.followup.send(
            "An error occurred while fetching branches. Please try again later.",
            ephemeral=True
        )


@bot.tree.command(name="status", description="Get repository activity summary")
async def get_status(interaction: discord.Interaction):
    """
    Get repository activity summary including commits, PRs, and issues.

    Args:
        interaction: Discord interaction object
    """
    await interaction.response.defer()

    try:
        status = bot.github.get_repository_status()
        if status:
            embed = MessageFormatter.format_repository_status(status)
            await interaction.followup.send(embed=embed)
            logger.info(f"User {interaction.user} requested repository status")
        else:
            await interaction.followup.send(
                "An error occurred while fetching repository status.",
                ephemeral=True
            )
    except Exception as e:
        logger.error(f"Error in /status command: {e}")
        await interaction.followup.send(
            "An error occurred while fetching repository status. Please try again later.",
            ephemeral=True
        )


@bot.tree.command(name="assign", description="Request a PR review from a team member")
@app_commands.describe(
    user="Discord user to request review from",
    pr_number="Pull request number"
)
async def assign_reviewer(interaction: discord.Interaction, user: discord.Member, pr_number: int):
    """
    Request a PR review from a team member.

    Args:
        interaction: Discord interaction object
        user: Discord member to ping
        pr_number: Pull request number
    """
    try:
        # Get PR information to include in the message
        pr = bot.github.get_pull_request(pr_number)

        if pr:
            embed = discord.Embed(
                title=f"Review Request for PR #{pr_number}",
                description=f"**{pr['title']}**\n\n{user.mention}, you've been requested to review this pull request.",
                color=MessageFormatter.COLOR_ORANGE,
                url=pr['url']
            )
            embed.add_field(name="Author", value=pr['author'], inline=True)
            embed.add_field(name="Branch", value=f"`{pr['branch']}`", inline=True)
            embed.add_field(
                name="Changes",
                value=f"+{pr['additions']} -{pr['deletions']} ({pr['files_changed']} files)",
                inline=True
            )
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)
            logger.info(f"User {interaction.user} requested review from {user} for PR #{pr_number}")
        else:
            await interaction.response.send_message(
                f"Pull request #{pr_number} not found.",
                ephemeral=True
            )
    except Exception as e:
        logger.error(f"Error in /assign command: {e}")
        await interaction.response.send_message(
            "An error occurred while processing your request. Please try again later.",
            ephemeral=True
        )


async def main():
    """Main function to run the bot."""
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        return

    # Start the bot
    try:
        await bot.start(Config.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())
