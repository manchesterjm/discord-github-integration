# GitHub-Discord Integration Bot

A Discord bot that integrates with GitHub to help teams coordinate their software development projects. The bot provides real-time notifications about GitHub activity and interactive commands to track pull requests, commits, and project status.

## Features

### Real-time GitHub Notifications
- New commits pushed to branches
- Pull requests opened, closed, or merged
- Pull request reviews (approved, changes requested, commented)
- Issues opened or closed
- Branches created or deleted

### Discord Slash Commands
- `/prs` - List all open pull requests with status
- `/pr <number>` - Get detailed info about a specific PR
- `/commits <branch>` - Show recent commits on a branch (default: main)
- `/branches` - List all active branches
- `/status` - Repository activity summary (commits today, open PRs, open issues)
- `/assign <@user> <pr_number>` - Request PR review from team member

## Prerequisites

- **Python 3.9 or higher**
- **Discord Bot Token** - [Create a bot](https://discord.com/developers/applications)
- **GitHub Personal Access Token** - [Generate token](https://github.com/settings/tokens)
  - Required scopes: `repo` (full control of private repositories)
- **A Discord Server** where you have admin permissions
- **A publicly accessible URL** for receiving webhooks (use ngrok for local development)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd github-discord-bot
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_server_id_here
DISCORD_CHANNEL_ID=channel_id_for_github_notifications
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=owner/repository_name
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
FLASK_PORT=5000
```

## Configuration Guide

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Server Members Intent
   - Message Content Intent
5. Copy the bot token and save it as `DISCORD_BOT_TOKEN` in `.env`
6. Go to "OAuth2" > "URL Generator"
7. Select scopes:
   - `bot`
   - `applications.commands`
8. Select bot permissions:
   - Send Messages
   - Embed Links
   - Mention Everyone
   - Use Slash Commands
9. Copy the generated URL and use it to invite the bot to your server

### Getting Discord IDs

1. Enable Developer Mode in Discord:
   - User Settings > Advanced > Developer Mode (toggle ON)
2. Get Server ID:
   - Right-click your server name > Copy ID
   - Save as `DISCORD_GUILD_ID` in `.env`
3. Get Channel ID:
   - Right-click the channel for notifications > Copy ID
   - Save as `DISCORD_CHANNEL_ID` in `.env`

### GitHub Token Setup

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Discord Bot")
4. Select scopes:
   - `repo` (Full control of private repositories)
5. Click "Generate token"
6. Copy the token immediately and save it as `GITHUB_TOKEN` in `.env`
7. Set `GITHUB_REPO` to your repository in format `owner/repository`

### GitHub Webhook Setup

1. Generate a secure webhook secret:
   ```bash
   # On Linux/macOS
   openssl rand -hex 32

   # On Windows (PowerShell)
   -join ((48..57) + (65..70) | Get-Random -Count 32 | % {[char]$_})
   ```
   Save this as `GITHUB_WEBHOOK_SECRET` in `.env`

2. Go to your GitHub repository
3. Navigate to Settings > Webhooks > Add webhook
4. Configure the webhook:
   - **Payload URL**: `https://your-server-url.com/webhook`
     - For local testing, use [ngrok](https://ngrok.com/): `ngrok http 5000`
   - **Content type**: `application/json`
   - **Secret**: Paste your `GITHUB_WEBHOOK_SECRET`
   - **Events**: Select individual events:
     - Pushes
     - Pull requests
     - Pull request reviews
     - Pull request review comments
     - Issues
     - Branch or tag creation
     - Branch or tag deletion
   - **Active**: Checked
5. Click "Add webhook"

## Running the Bot

### Run Both Bot and Webhook Server

The easiest way to run everything:

```bash
python main.py
```

This starts both the Discord bot and the webhook server concurrently.

### Run Components Separately (for development)

**Terminal 1 - Discord Bot:**
```bash
python bot.py
```

**Terminal 2 - Webhook Server:**
```bash
python webhook_server.py
```

### For Local Development with ngrok

1. Start ngrok:
   ```bash
   ngrok http 5000
   ```

2. Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.io`)

3. Use this URL when setting up the GitHub webhook:
   ```
   https://abc123.ngrok.io/webhook
   ```

4. Start the bot:
   ```bash
   python main.py
   ```

## Deployment

### Deploying to Railway

1. Create a [Railway](https://railway.app/) account
2. Create a new project from GitHub
3. Add environment variables in Railway dashboard (all variables from `.env`)
4. Railway will automatically deploy your bot
5. Use the Railway-provided URL for your webhook

### Deploying to Render

1. Create a [Render](https://render.com/) account
2. Create a new Web Service from your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. Add environment variables in Render dashboard
5. Use the Render-provided URL for your webhook

### Deploying to a VPS

1. SSH into your server
2. Clone the repository
3. Install Python 3.9+
4. Set up a virtual environment and install dependencies
5. Create `.env` file with your configuration
6. Use a process manager like systemd:

Create `/etc/systemd/system/github-discord-bot.service`:

```ini
[Unit]
Description=GitHub Discord Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/github-discord-bot
Environment="PATH=/path/to/github-discord-bot/venv/bin"
ExecStart=/path/to/github-discord-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable github-discord-bot
sudo systemctl start github-discord-bot
```

## Usage Examples

### List Open Pull Requests
```
/prs
```
Displays all open pull requests with their status, reviewers, and age.

### Get PR Details
```
/pr 42
```
Shows detailed information about pull request #42 including description, changes, and review status.

### View Recent Commits
```
/commits main
```
Shows the 10 most recent commits on the main branch.

### Check Repository Status
```
/status
```
Displays a summary of today's activity, open PRs, open issues, and branch count.

### Request a Review
```
/assign @teammate 42
```
Pings @teammate to review pull request #42.

## Troubleshooting

### Bot is not responding to commands
- Make sure the bot is online (check Discord status)
- Verify the bot has proper permissions in your server
- Check that you've enabled the required intents in Discord Developer Portal
- Look at the logs in `bot.log`

### Webhooks are not being received
- Verify your webhook URL is publicly accessible
- Check that the webhook secret matches in both GitHub and `.env`
- Look at webhook delivery logs in GitHub (Settings > Webhooks > Recent Deliveries)
- Verify the Flask server is running on the correct port

### Commands show "Application did not respond"
- The bot might be taking too long to respond
- Check for errors in `bot.log`
- Verify your GitHub token has the correct permissions
- Ensure the repository name is in the correct format (`owner/repo`)

### Configuration Validation Failed
- Make sure all required environment variables are set in `.env`
- Check that `GITHUB_REPO` is in format `owner/repository`
- Verify all tokens are valid and not expired

## Project Structure

```
github-discord-bot/
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── CLAUDE.md              # Project specification
├── main.py                # Main entry point (runs bot + webhook server)
├── bot.py                 # Discord bot with slash commands
├── webhook_server.py      # Flask server for GitHub webhooks
├── config.py              # Configuration management
└── utils/
    ├── __init__.py
    ├── github_api.py      # GitHub API helper functions
    └── formatters.py      # Discord message formatting
```

## Contributing

This is a college project for an Advanced Software Engineering course. Contributions from team members are welcome!

### Development Workflow
1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Create a pull request
5. Use `/assign` to request review from a teammate
6. Merge after approval

## Security Notes

- **Never commit your `.env` file** - it contains sensitive tokens
- **Keep your tokens secure** - don't share them publicly
- **Use webhook signatures** - the bot validates all GitHub webhooks
- **Regular token rotation** - periodically regenerate your tokens
- **Limit token scopes** - only grant necessary permissions

## Team Members

- Team Member 1 - Role
- Team Member 2 - Role
- Team Member 3 - Role
- Team Member 4 - Role

## License

This project is for educational purposes as part of an Advanced Software Engineering course.

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- GitHub integration via [PyGithub](https://github.com/PyGithub/PyGithub)
- Webhook server with [Flask](https://flask.palletsprojects.com/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs in `bot.log`
3. Consult the [discord.py documentation](https://discordpy.readthedocs.io/)
4. Check [PyGithub documentation](https://pygithub.readthedocs.io/)

---

**Happy Coding!**
