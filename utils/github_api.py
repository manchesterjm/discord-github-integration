"""
GitHub API helper functions for interacting with the GitHub API.

This module provides a wrapper around PyGithub to simplify common operations
like fetching pull requests, commits, branches, and issues.
"""

from github import Github, GithubException
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class GitHubAPI:
    """Wrapper class for GitHub API interactions."""

    def __init__(self, token: str, repo_name: str):
        """
        Initialize the GitHub API client.

        Args:
            token: GitHub personal access token
            repo_name: Repository name in format 'owner/repo'
        """
        self.client = Github(token)
        self.repo = self.client.get_repo(repo_name)
        logger.info(f"GitHub API initialized for repository: {repo_name}")

    def get_open_pull_requests(self) -> List[Dict[str, Any]]:
        """
        Get all open pull requests for the repository.

        Returns:
            List of dictionaries containing PR information.
        """
        try:
            pulls = self.repo.get_pulls(state='open', sort='created', direction='desc')
            pr_list = []

            for pr in pulls:
                # Get review information
                reviews = pr.get_reviews()
                reviewers = {}
                for review in reviews:
                    reviewer = review.user.login
                    state = review.state
                    reviewers[reviewer] = state

                # Calculate age
                age = datetime.now() - pr.created_at.replace(tzinfo=None)
                age_str = self._format_timedelta(age)

                pr_list.append({
                    'number': pr.number,
                    'title': pr.title,
                    'author': pr.user.login,
                    'branch': f"{pr.head.ref} -> {pr.base.ref}",
                    'url': pr.html_url,
                    'created_at': pr.created_at,
                    'age': age_str,
                    'reviewers': reviewers,
                    'state': pr.state
                })

            logger.info(f"Retrieved {len(pr_list)} open pull requests")
            return pr_list

        except GithubException as e:
            logger.error(f"Error fetching pull requests: {e}")
            return []

    def get_pull_request(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific pull request.

        Args:
            pr_number: Pull request number

        Returns:
            Dictionary containing PR information, or None if not found.
        """
        try:
            pr = self.repo.get_pull(pr_number)

            # Get review information
            reviews = pr.get_reviews()
            reviewers = {}
            for review in reviews:
                reviewer = review.user.login
                state = review.state
                reviewers[reviewer] = state

            # Get file changes
            files_changed = pr.changed_files
            additions = pr.additions
            deletions = pr.deletions

            # Calculate age
            age = datetime.now() - pr.created_at.replace(tzinfo=None)
            age_str = self._format_timedelta(age)

            pr_info = {
                'number': pr.number,
                'title': pr.title,
                'author': pr.user.login,
                'branch': f"{pr.head.ref} -> {pr.base.ref}",
                'url': pr.html_url,
                'state': pr.state,
                'created_at': pr.created_at,
                'age': age_str,
                'reviewers': reviewers,
                'files_changed': files_changed,
                'additions': additions,
                'deletions': deletions,
                'body': pr.body or 'No description provided.',
                'mergeable': pr.mergeable,
                'merged': pr.merged
            }

            logger.info(f"Retrieved pull request #{pr_number}")
            return pr_info

        except GithubException as e:
            logger.error(f"Error fetching pull request #{pr_number}: {e}")
            return None

    def get_commits(self, branch: str = 'main', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent commits for a specific branch.

        Args:
            branch: Branch name (default: 'main')
            limit: Maximum number of commits to retrieve (default: 10)

        Returns:
            List of dictionaries containing commit information.
        """
        try:
            commits = self.repo.get_commits(sha=branch)[:limit]
            commit_list = []

            for commit in commits:
                commit_list.append({
                    'sha': commit.sha[:7],
                    'message': commit.commit.message.split('\n')[0],  # First line only
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date,
                    'url': commit.html_url
                })

            logger.info(f"Retrieved {len(commit_list)} commits from branch '{branch}'")
            return commit_list

        except GithubException as e:
            logger.error(f"Error fetching commits for branch '{branch}': {e}")
            return []

    def get_branches(self) -> List[Dict[str, str]]:
        """
        Get all branches in the repository.

        Returns:
            List of dictionaries containing branch information.
        """
        try:
            branches = self.repo.get_branches()
            branch_list = []

            for branch in branches:
                branch_list.append({
                    'name': branch.name,
                    'protected': branch.protected
                })

            logger.info(f"Retrieved {len(branch_list)} branches")
            return branch_list

        except GithubException as e:
            logger.error(f"Error fetching branches: {e}")
            return []

    def get_repository_status(self) -> Dict[str, Any]:
        """
        Get overall repository status including commits, PRs, and issues.

        Returns:
            Dictionary containing repository status information.
        """
        try:
            # Get today's commits
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            commits_today = 0
            try:
                recent_commits = self.repo.get_commits(since=today)
                commits_today = recent_commits.totalCount
            except:
                commits_today = 0

            # Get open PRs count
            open_prs = self.repo.get_pulls(state='open').totalCount

            # Get open issues count
            open_issues = self.repo.get_issues(state='open').totalCount - open_prs  # Subtract PRs

            # Get branch count
            branches = self.repo.get_branches().totalCount

            status = {
                'repo_name': self.repo.full_name,
                'commits_today': commits_today,
                'open_prs': open_prs,
                'open_issues': open_issues,
                'branches': branches,
                'default_branch': self.repo.default_branch
            }

            logger.info("Retrieved repository status")
            return status

        except GithubException as e:
            logger.error(f"Error fetching repository status: {e}")
            return {}

    @staticmethod
    def _format_timedelta(td: timedelta) -> str:
        """
        Format a timedelta into a human-readable string.

        Args:
            td: Timedelta object

        Returns:
            Formatted string (e.g., '2 days', '3 hours', '45 minutes')
        """
        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60

        if days > 0:
            return f"{days} day{'s' if days != 1 else ''}"
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return "just now"
