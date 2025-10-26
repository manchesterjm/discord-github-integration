"""
Message formatting utilities for Discord embeds and notifications.

This module provides functions to format GitHub events into
well-structured Discord messages with embeds.
"""

import discord
from datetime import datetime
from typing import Dict, Any, List


class MessageFormatter:
    """Formatter class for creating Discord embeds from GitHub events."""

    # Color constants
    COLOR_BLUE = 0x0366d6
    COLOR_GREEN = 0x28a745
    COLOR_RED = 0xd73a49
    COLOR_PURPLE = 0x6f42c1
    COLOR_ORANGE = 0xfb8500

    @staticmethod
    def format_commit_notification(payload: Dict[str, Any]) -> discord.Embed:
        """
        Format a push event into a Discord embed.

        Args:
            payload: GitHub webhook payload for push event

        Returns:
            Discord embed object
        """
        ref = payload['ref'].split('/')[-1]  # Extract branch name
        commits = payload['commits']
        pusher = payload['pusher']['name']
        repo_name = payload['repository']['name']
        compare_url = payload['compare']

        # Get the first commit for display
        if commits:
            commit = commits[0]
            message = commit['message'].split('\n')[0][:100]  # First line, max 100 chars
            author = commit['author']['name']
            commit_url = commit['url']
        else:
            message = "No commit message"
            author = pusher
            commit_url = compare_url

        embed = discord.Embed(
            title=f"New Commit{'s' if len(commits) > 1 else ''} to `{ref}`",
            description=f"**{message}**",
            color=MessageFormatter.COLOR_BLUE,
            url=compare_url,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Author", value=author, inline=True)
        embed.add_field(name="Branch", value=f"`{ref}`", inline=True)
        embed.add_field(name="Commits", value=str(len(commits)), inline=True)
        embed.set_footer(text=f"{repo_name}")

        return embed

    @staticmethod
    def format_pull_request_notification(payload: Dict[str, Any]) -> discord.Embed:
        """
        Format a pull request event into a Discord embed.

        Args:
            payload: GitHub webhook payload for pull_request event

        Returns:
            Discord embed object
        """
        action = payload['action']
        pr = payload['pull_request']
        pr_number = pr['number']
        title = pr['title']
        author = pr['user']['login']
        branch = f"{pr['head']['ref']} -> {pr['base']['ref']}"
        url = pr['html_url']
        merged = pr.get('merged', False)

        # Determine emoji and status based on action
        if action == 'opened':
            emoji = ""
            status = "Awaiting Review"
            color = MessageFormatter.COLOR_BLUE
        elif action == 'closed' and merged:
            emoji = ""
            status = "Merged"
            color = MessageFormatter.COLOR_PURPLE
        elif action == 'closed':
            emoji = ""
            status = "Closed"
            color = MessageFormatter.COLOR_RED
        elif action == 'reopened':
            emoji = ""
            status = "Reopened"
            color = MessageFormatter.COLOR_ORANGE
        else:
            emoji = ""
            status = action.capitalize()
            color = MessageFormatter.COLOR_BLUE

        embed = discord.Embed(
            title=f"{emoji} Pull Request #{pr_number} {action.capitalize()}",
            description=f"**{title}**",
            color=color,
            url=url,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Author", value=author, inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Branch", value=f"`{branch}`", inline=False)

        if merged and 'merged_by' in pr and pr['merged_by']:
            embed.add_field(name="Merged by", value=pr['merged_by']['login'], inline=True)

        return embed

    @staticmethod
    def format_review_notification(payload: Dict[str, Any]) -> discord.Embed:
        """
        Format a pull request review event into a Discord embed.

        Args:
            payload: GitHub webhook payload for pull_request_review event

        Returns:
            Discord embed object
        """
        review = payload['review']
        pr = payload['pull_request']
        pr_number = pr['number']
        pr_title = pr['title']
        reviewer = review['user']['login']
        state = review['state']
        comment = review['body'] or "No comment provided"
        url = review['html_url']

        # Determine emoji and color based on review state
        if state == 'approved':
            emoji = ""
            status = "Approved"
            color = MessageFormatter.COLOR_GREEN
        elif state == 'changes_requested':
            emoji = ""
            status = "Changes Requested"
            color = MessageFormatter.COLOR_RED
        else:
            emoji = ""
            status = "Commented"
            color = MessageFormatter.COLOR_BLUE

        embed = discord.Embed(
            title=f"{emoji} Review on PR #{pr_number}",
            description=f"**{pr_title}**",
            color=color,
            url=url,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Reviewer", value=reviewer, inline=True)
        embed.add_field(name="Status", value=status, inline=True)

        # Truncate comment if too long
        if len(comment) > 200:
            comment = comment[:197] + "..."
        embed.add_field(name="Comment", value=comment, inline=False)

        return embed

    @staticmethod
    def format_issue_notification(payload: Dict[str, Any]) -> discord.Embed:
        """
        Format an issue event into a Discord embed.

        Args:
            payload: GitHub webhook payload for issues event

        Returns:
            Discord embed object
        """
        action = payload['action']
        issue = payload['issue']
        issue_number = issue['number']
        title = issue['title']
        author = issue['user']['login']
        url = issue['html_url']

        # Determine emoji and color based on action
        if action == 'opened':
            emoji = ""
            color = MessageFormatter.COLOR_GREEN
        elif action == 'closed':
            emoji = ""
            color = MessageFormatter.COLOR_RED
        else:
            emoji = ""
            color = MessageFormatter.COLOR_BLUE

        embed = discord.Embed(
            title=f"{emoji} Issue #{issue_number} {action.capitalize()}",
            description=f"**{title}**",
            color=color,
            url=url,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Author", value=author, inline=True)

        return embed

    @staticmethod
    def format_branch_notification(payload: Dict[str, Any], deleted: bool = False) -> discord.Embed:
        """
        Format a branch creation/deletion event into a Discord embed.

        Args:
            payload: GitHub webhook payload for create/delete event
            deleted: Whether this is a deletion event

        Returns:
            Discord embed object
        """
        ref_type = payload.get('ref_type', 'branch')
        ref = payload.get('ref', 'unknown')
        sender = payload['sender']['login']

        if deleted:
            emoji = ""
            action = "Deleted"
            color = MessageFormatter.COLOR_RED
        else:
            emoji = ""
            action = "Created"
            color = MessageFormatter.COLOR_GREEN

        embed = discord.Embed(
            title=f"{emoji} {ref_type.capitalize()} {action}",
            description=f"**`{ref}`**",
            color=color,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="By", value=sender, inline=True)

        return embed

    @staticmethod
    def format_pr_list(prs: List[Dict[str, Any]]) -> discord.Embed:
        """
        Format a list of pull requests into a Discord embed.

        Args:
            prs: List of pull request dictionaries

        Returns:
            Discord embed object
        """
        if not prs:
            embed = discord.Embed(
                title="Open Pull Requests",
                description="No open pull requests found.",
                color=MessageFormatter.COLOR_BLUE
            )
            return embed

        embed = discord.Embed(
            title=f"Open Pull Requests ({len(prs)})",
            color=MessageFormatter.COLOR_BLUE,
            timestamp=datetime.utcnow()
        )

        for pr in prs[:10]:  # Limit to 10 PRs to avoid embed limits
            reviewers_text = ""
            if pr['reviewers']:
                reviewer_states = []
                for reviewer, state in pr['reviewers'].items():
                    if state == 'APPROVED':
                        reviewer_states.append(f"{reviewer} ")
                    elif state == 'CHANGES_REQUESTED':
                        reviewer_states.append(f"{reviewer} ")
                    else:
                        reviewer_states.append(f"{reviewer} ")
                reviewers_text = f"\nReviewers: {', '.join(reviewer_states)}"

            field_value = (
                f"Author: {pr['author']} | Age: {pr['age']}\n"
                f"Branch: `{pr['branch']}`"
                f"{reviewers_text}"
            )

            embed.add_field(
                name=f"PR #{pr['number']}: {pr['title'][:50]}",
                value=field_value,
                inline=False
            )

        if len(prs) > 10:
            embed.set_footer(text=f"Showing 10 of {len(prs)} pull requests")

        return embed

    @staticmethod
    def format_pr_detail(pr: Dict[str, Any]) -> discord.Embed:
        """
        Format detailed pull request information into a Discord embed.

        Args:
            pr: Pull request dictionary

        Returns:
            Discord embed object
        """
        # Determine color based on state
        if pr['merged']:
            color = MessageFormatter.COLOR_PURPLE
            status = " Merged"
        elif pr['state'] == 'closed':
            color = MessageFormatter.COLOR_RED
            status = " Closed"
        else:
            color = MessageFormatter.COLOR_BLUE
            status = " Open - Awaiting Review"

        embed = discord.Embed(
            title=f"PR #{pr['number']}: {pr['title']}",
            description=pr['body'][:200] + "..." if len(pr['body']) > 200 else pr['body'],
            color=color,
            url=pr['url'],
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Author", value=pr['author'], inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Age", value=pr['age'], inline=True)
        embed.add_field(name="Branch", value=f"`{pr['branch']}`", inline=False)
        embed.add_field(
            name="Changes",
            value=f"+{pr['additions']} -{pr['deletions']} ({pr['files_changed']} files)",
            inline=True
        )

        if pr['reviewers']:
            reviewer_list = []
            for reviewer, state in pr['reviewers'].items():
                if state == 'APPROVED':
                    reviewer_list.append(f" {reviewer}")
                elif state == 'CHANGES_REQUESTED':
                    reviewer_list.append(f" {reviewer}")
                else:
                    reviewer_list.append(f" {reviewer}")
            embed.add_field(name="Reviewers", value="\n".join(reviewer_list), inline=True)

        return embed

    @staticmethod
    def format_commit_list(commits: List[Dict[str, Any]], branch: str) -> discord.Embed:
        """
        Format a list of commits into a Discord embed.

        Args:
            commits: List of commit dictionaries
            branch: Branch name

        Returns:
            Discord embed object
        """
        if not commits:
            embed = discord.Embed(
                title=f"Recent Commits on `{branch}`",
                description="No commits found.",
                color=MessageFormatter.COLOR_BLUE
            )
            return embed

        embed = discord.Embed(
            title=f"Recent Commits on `{branch}`",
            color=MessageFormatter.COLOR_BLUE,
            timestamp=datetime.utcnow()
        )

        for commit in commits:
            embed.add_field(
                name=f"`{commit['sha']}` - {commit['author']}",
                value=commit['message'][:100],
                inline=False
            )

        return embed

    @staticmethod
    def format_repository_status(status: Dict[str, Any]) -> discord.Embed:
        """
        Format repository status into a Discord embed.

        Args:
            status: Repository status dictionary

        Returns:
            Discord embed object
        """
        embed = discord.Embed(
            title=f"Repository Status - {status['repo_name']}",
            color=MessageFormatter.COLOR_GREEN,
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name=" Today's Activity",
            value=f"{status['commits_today']} commits",
            inline=True
        )
        embed.add_field(
            name=" Open PRs",
            value=str(status['open_prs']),
            inline=True
        )
        embed.add_field(
            name=" Open Issues",
            value=str(status['open_issues']),
            inline=True
        )
        embed.add_field(
            name=" Active Branches",
            value=str(status['branches']),
            inline=True
        )
        embed.add_field(
            name=" Default Branch",
            value=f"`{status['default_branch']}`",
            inline=True
        )

        return embed

    @staticmethod
    def format_branch_list(branches: List[Dict[str, str]]) -> discord.Embed:
        """
        Format a list of branches into a Discord embed.

        Args:
            branches: List of branch dictionaries

        Returns:
            Discord embed object
        """
        if not branches:
            embed = discord.Embed(
                title="Active Branches",
                description="No branches found.",
                color=MessageFormatter.COLOR_BLUE
            )
            return embed

        embed = discord.Embed(
            title=f"Active Branches ({len(branches)})",
            color=MessageFormatter.COLOR_GREEN,
            timestamp=datetime.utcnow()
        )

        branch_text = []
        for branch in branches[:25]:  # Limit to avoid embed limits
            protected = " " if branch['protected'] else ""
            branch_text.append(f"`{branch['name']}`{protected}")

        # Split into chunks to avoid field value limits
        chunk_size = 10
        for i in range(0, len(branch_text), chunk_size):
            chunk = branch_text[i:i+chunk_size]
            embed.add_field(
                name="\u200b",  # Zero-width space for blank field name
                value="\n".join(chunk),
                inline=True
            )

        if len(branches) > 25:
            embed.set_footer(text=f"Showing 25 of {len(branches)} branches")

        return embed
