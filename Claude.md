# GitHub-Discord Integration Bot - Project Specification

## Project Overview
Build a Discord bot that integrates with GitHub to help a team of 4 college students coordinate their Advanced Software Engineering project. The bot will provide real-time notifications about GitHub activity and help track pull requests, commits, and project status.

## Technical Stack
- **Language**: Python 3.9+
- **Discord Library**: discord.py (v2.x)
- **GitHub Integration**: PyGithub library
- **Web Framework**: Flask (for webhook receiving)
- **Environment Management**: python-dotenv
- **Deployment**: Designed to run 24/7 (Railway, Render, or local server)

## Project Structure
```
github-discord-bot/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── bot.py (main Discord bot)
├── webhook_server.py (Flask server for GitHub webhooks)
├── config.py (configuration management)
└── utils/
    ├── __init__.py
    ├── github_api.py (GitHub API helpers)
    └── formatters.py (message formatting utilities)
```

## Core Features to Implement

### Phase 1: Basic Bot Setup
1. Discord bot connection and basic commands
2. Proper configuration management with environment variables
3. Error handling and logging

### Phase 2: GitHub Webhook Integration
1. Flask server to receive GitHub webhooks
2. Webhook signature verification for security
3. Parse and format webhook payloads
4. Send formatted messages to designated Discord channel

### Phase 3: Webhook Event Handlers
Handle these GitHub events:
- **push**: New commits to any branch
- **pull_request**: PR opened, closed, merged, reopened
- **pull_request_review**: Reviews submitted, approved, changes requested
- **pull_request_review_comment**: Comments on PR code
- **issues**: Issues opened, closed, commented
- **create**: Branch or tag created
- **delete**: Branch or tag deleted

### Phase 4: Discord Commands
Implement these slash commands:
- `/prs` - List all open pull requests with status
- `/pr <number>` - Get detailed info about a specific PR
- `/commits <branch>` - Show recent commits on a branch
- `/branches` - List all active branches
- `/status` - Repository activity summary (commits today, open PRs, open issues)
- `/assign <@user> <pr_number>` - Request PR review from team member

### Phase 5: Advanced Features (Optional)
- Daily standup reminder with GitHub activity summary
- Stale PR notifications (PRs open >48 hours without review)
- Congratulatory messages for merged PRs
- GitHub issue tracking integration

## Detailed Requirements

### Environment Variables (.env)
```
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_server_id
DISCORD_CHANNEL_ID=channel_for_github_notifications
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=owner/repository_name
GITHUB_WEBHOOK_SECRET=your_webhook_secret
FLASK_PORT=5000
```

### Discord Bot Setup
1. Bot needs these intents: guilds, guild_messages, message_content
2. Bot permissions: Send Messages, Embed Links, Mention Everyone
3. Use application commands (slash commands) for better UX
4. Implement proper error handling and logging
5. Use embeds for rich message formatting

### GitHub Webhook Configuration
1. Set up webhook at: `https://github.com/{owner}/{repo}/settings/hooks`
2. Payload URL: Your server's public URL + `/webhook` endpoint
3. Content type: `application/json`
4. Secret: Generate a secure random string
5. Events to subscribe:
   - Pushes
   - Pull requests
   - Pull request reviews
   - Pull request review comments
   - Issues
   - Branch or tag creation
   - Branch or tag deletion

### Security Requirements
1. **Webhook signature verification**: Verify GitHub webhook signatures using HMAC-SHA256
2. **Token security**: Never commit tokens to Git, use .env files
3. **Input validation**: Validate all webhook payloads and command inputs
4. **Rate limiting**: Implement basic rate limiting on commands

### Message Formatting Guidelines

#### Commit Notification Format
```
🔨 New Commit to `main`
Author: @username
Message: "Fix bug in authentication flow"
Changes: +42 -15 (3 files)
[View Commit](link)
```

#### Pull Request Notification Format
```
🔀 Pull Request #42 Opened
Title: Add user authentication
Author: @username
Branch: feature/auth -> main
Status: ⏳ Awaiting Review
[View PR](link)
```

#### PR Merge Format
```
✅ Pull Request #42 Merged
Title: Add user authentication
Author: @username
Merged by: @reviewer
[View PR](link)
```

#### Review Notification Format
```
👀 Review on PR #42
Reviewer: @username
Status: ✅ Approved / ⚠️ Changes Requested / 💬 Commented
Comment: "Looks good, just minor styling issues"
[View Review](link)
```

### Command Response Formats

#### `/prs` Command Response
Use Discord embed with:
- Title: "Open Pull Requests (3)"
- Color: Blue (#0366d6)
- Fields for each PR:
  - PR #42: Add user authentication
  - Author: @username | Status: ⏳ Awaiting Review | Age: 2 days
  - Reviewers: @user1 (approved), @user2 (pending)

#### `/status` Command Response
Use Discord embed with:
- Title: "Repository Status - [Repo Name]"
- Color: Green (#28a745)
- Fields:
  - 📊 Today's Activity: X commits, Y PRs opened
  - 🔀 Open PRs: Z pull requests
  - 🐛 Open Issues: W issues
  - 🌿 Active Branches: V branches

### Error Handling
1. Log all errors with timestamps and context
2. Send user-friendly error messages in Discord
3. Implement retry logic for GitHub API calls
4. Handle Discord rate limits gracefully
5. Validate webhook payloads before processing

### Testing Considerations
1. Test all webhook event types
2. Test slash commands with various inputs
3. Test error scenarios (invalid PR numbers, API failures)
4. Test with multiple team members simultaneously
5. Verify webhook signature validation works

### Deployment Requirements
1. Bot must run 24/7 to receive webhooks
2. Webhook server must be publicly accessible
3. Use environment variables for all secrets
4. Implement logging for debugging
5. Consider using a process manager (systemd, PM2, or platform-specific)

### Documentation to Include

#### README.md should contain:
1. Project description and purpose
2. Prerequisites (Python version, Discord bot creation, GitHub token)
3. Installation steps
4. Configuration guide
5. How to set up GitHub webhooks
6. Available commands and their usage
7. Deployment instructions
8. Team member information

#### .env.example should contain:
All required environment variables with placeholder values and comments explaining each

### Code Quality Standards
1. Follow PEP 8 style guidelines
2. Add docstrings to all functions and classes
3. Use type hints for function parameters and returns
4. Implement proper async/await patterns
5. Add comments for complex logic
6. Keep functions focused and single-purpose

## Implementation Order
1. Set up project structure and install dependencies
2. Create basic Discord bot with connection test
3. Implement Flask webhook server with signature verification
4. Add GitHub webhook event handlers one by one
5. Implement slash commands
6. Add message formatting and embeds
7. Implement error handling and logging
8. Test all features thoroughly
9. Write comprehensive README
10. Prepare for deployment

## Success Criteria
- Bot successfully connects to Discord server
- Receives and processes all configured GitHub webhook events
- All slash commands work correctly
- Messages are well-formatted and informative
- No crashes or unhandled exceptions
- Secure handling of tokens and secrets
- Clear documentation for team setup

## Additional Notes for Claude Code
- Use async/await throughout for Discord.py
- Implement proper logging (use Python's logging module)
- Consider using Discord's cog system for organizing commands
- Make the bot easy to configure for different repositories
- Prioritize reliability and error recovery
- Keep the codebase clean and maintainable for the college team
- Add helpful comments for learning purposes since this is a college project

## Team Context
This bot is for a team of 4 college students working on an Advanced Software Engineering project. They currently use a Discord group chat but need better GitHub coordination. The bot should be straightforward to set up and maintain, well-documented for educational purposes, and reliable enough for daily use throughout their semester project.
