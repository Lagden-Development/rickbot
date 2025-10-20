<div align="center">

# 🤖 RickBot 2.0

### Production-grade Discord bot framework with database-first observability

[![GitHub Release](https://img.shields.io/github/v/release/Lagden-Development/rickbot)](https://github.com/Lagden-Development/rickbot/releases)
[![GitHub branch check runs](https://img.shields.io/github/check-runs/Lagden-Development/rickbot/main)](https://github.com/Lagden-Development/rickbot/actions)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d20be7f7ddcf429bb59329b97cee6903)](https://app.codacy.com/gh/Lagden-Development/rickbot/dashboard)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/github/license/Lagden-Development/rickbot)](https://unlicense.org/)
[![GitHub Stars](https://img.shields.io/github/stars/Lagden-Development/rickbot?style=social)](https://github.com/Lagden-Development/rickbot/stargazers)

</div>

---

A modern, type-safe Discord bot built with discord.py, featuring comprehensive command logging, error tracking, and performance metrics powered by MongoDB.

## ✨ Features

- **Slash Commands** - Modern Discord interactions with autocomplete and modals
- **Database-First Observability** - Track every command, error, and metric
- **Type-Safe Configuration** - Pydantic-powered YAML config with environment variables
- **Production Ready** - Graceful shutdown, structured logging, and error handling
- **Beautiful Console Output** - Colored logs and startup banners
- **Moderation Tools** - Kick, ban, timeout, purge, and more
- **Developer Tools** - Hot reloading, error viewer, metrics dashboard
- **Extensible** - Easy-to-add cogs with example implementations

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- MongoDB 4.4 or higher (local or Atlas)
- A Discord bot token ([Get one here](https://discord.com/developers/applications))

### Installation

<details>
<summary><b>Click to expand installation steps</b></summary>

#### 1. **Clone the repository**

```bash
git clone https://github.com/Lagden-Development/rickbot.git
cd rickbot
```

#### 2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. **Install dependencies**

```bash
pip install -r requirements.txt
```

#### 4. **Set up environment variables**

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_bot_token_here
MONGO_URI=mongodb://localhost:27017
```

> **⚠️ SECURITY WARNING:** Never commit your `.env` file to version control! It contains sensitive credentials.

#### 5. **Configure the bot**

Copy the example configuration:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` and set:
- `application_id`: Your bot's application ID (from Discord Developer Portal)
- `dev_guild_id`: (Optional) Your test server ID for instant command syncing
- `owner_ids`: List of user IDs who can use owner-only commands

#### 6. **Run the bot**

```bash
python app.py
```

</details>

## ⚙️ Configuration

### Environment Variables

The bot uses environment variables for sensitive data. Set these in your `.env` file:

| Variable | Description | Required |
|:---------|:------------|:--------:|
| `DISCORD_TOKEN` | Your Discord bot token | ✅ Yes |
| `MONGO_URI` | MongoDB connection string | ✅ Yes |

### Configuration File

The `config.yaml` file controls all bot behavior. Key sections:

<details>
<summary><b>Bot Settings</b></summary>

```yaml
bot:
  token: ${DISCORD_TOKEN}              # Bot token (from .env)
  application_id: 123456789012345678   # Your app ID
  dev_guild_id: null                   # Test server (optional)
  owner_ids: []                        # Owner user IDs
  status_text: "Ready for commands"    # Bot status
  status_type: "playing"               # playing, watching, listening, competing
  sync_commands_on_ready: true         # Auto-sync commands
```

</details>

<details>
<summary><b>Discord Intents</b></summary>

```yaml
intents:
  guilds: true              # ✅ Required
  guild_messages: true      # ✅ Required for message commands
  message_content: false    # ⚠️ Privileged (not needed for slash-only bots)
  members: false            # ⚠️ Privileged
  presences: false          # ⚠️ Privileged
```

> **Note:** Privileged intents must be enabled in the [Discord Developer Portal](https://discord.com/developers/applications).

</details>

<details>
<summary><b>MongoDB Settings</b></summary>

```yaml
mongodb:
  uri: ${MONGO_URI}              # Connection string
  database: "rickbot"            # Database name
  pool_size: 10                  # Connection pool size
  timeout_ms: 5000               # Connection timeout
  retry_writes: true             # Enable retry writes
```

</details>

<details>
<summary><b>Observability</b></summary>

```yaml
observability:
  track_command_execution: true   # Log all commands
  track_command_timing: true      # Record execution time
  track_command_args: true        # ⚠️ Log arguments (may contain PII)
  track_errors: true              # Log errors to database
  store_error_traceback: true     # Store full stack traces
  aggregate_metrics_interval: 300 # Metric snapshots every 5 minutes
```

</details>

## 🗄️ MongoDB Setup

<details>
<summary><b>Local Installation</b></summary>

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
Download from [mongodb.com](https://www.mongodb.com/try/download/community)

</details>

<details>
<summary><b>MongoDB Atlas (Cloud)</b></summary>

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas)
2. Get your connection string
3. Set in `.env`: `MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/`

</details>

## 📝 Commands

### User Commands

| Command | Description |
|:--------|:------------|
| `/ping` | Check bot latency |
| `/info` | View bot information and statistics |
| `/stats` | Detailed command usage statistics |
| `/uptime` | Bot uptime and performance metrics |

### Admin Commands (Requires Permissions)

| Command | Description | Permission |
|:--------|:------------|:-----------|
| `/kick` | Kick a member | Kick Members |
| `/ban` | Ban a member or user | Ban Members |
| `/unban` | Unban a user | Ban Members |
| `/timeout` | Timeout a member | Moderate Members |
| `/untimeout` | Remove timeout | Moderate Members |
| `/purge` | Delete multiple messages | Manage Messages |
| `/slowmode` | Set channel slowmode | Manage Channels |

### Owner Commands

| Command | Description |
|:--------|:------------|
| `/reload` | Hot reload a cog |
| `/sync` | Sync slash commands |
| `/errors` | View error logs from database |
| `/metrics` | View performance metrics |
| `/dbstats` | View database statistics |

## 🛠️ Development

<details>
<summary><b>Project Structure</b></summary>

```
rickbot/
├── app.py                 # Application entry point
├── config.yaml            # Configuration file
├── .env                   # Environment variables (create this!)
├── core/                  # Core bot functionality
│   ├── bot.py            # Main bot class
│   ├── config.py         # Configuration system
│   ├── database.py       # MongoDB integration
│   ├── models.py         # Pydantic models
│   └── observability.py  # Command/error tracking
├── cogs/                  # Command modules
│   ├── admin.py          # Moderation commands
│   ├── botinfo.py        # Bot information commands
│   ├── devtools.py       # Developer utilities
│   └── examples/         # Example implementations
├── helpers/               # Utility functions
│   ├── logger.py         # Colored logging
│   ├── checks.py         # Permission checks
│   ├── colors.py         # Embed colors
│   └── ui.py             # UI components
└── requirements.txt       # Python dependencies
```

</details>

<details>
<summary><b>Creating a New Cog</b></summary>

1. Create a new file in `cogs/` (e.g., `mycog.py`)
2. Use this template:

```python
"""
Your cog description here.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.bot import RickBot


class MyCog(commands.Cog):
    """Cog description"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

    @app_commands.command(name="mycommand", description="Command description")
    async def my_command(self, interaction: discord.Interaction):
        """Your command implementation"""
        await interaction.response.send_message("Hello!")


async def setup(bot: "RickBot"):
    """Load the cog"""
    await bot.add_cog(MyCog(bot))
```

3. The bot will automatically load it on startup

</details>

### Hot Reloading

During development, use `/reload <cog_name>` to reload cogs without restarting:

```
/reload cogs.mycog
```

### Code Formatting

The project uses Black for code formatting:

```bash
black .
```

## 💾 Database Collections

<details>
<summary><b>Click to view database collections</b></summary>

The bot uses these MongoDB collections:

| Collection | Purpose |
|:-----------|:--------|
| `command_logs` | Every command execution with timing and args |
| `error_logs` | Detailed error information with tracebacks |
| `metrics` | Periodic snapshots of bot performance |
| `guild_settings` | Per-guild configuration (extensible) |

### Viewing Data

Use MongoDB Compass or the mongo shell:

```bash
mongosh
use rickbot
db.command_logs.find().limit(5).pretty()
db.error_logs.find({resolved: false}).pretty()
```

</details>

## 🚢 Production Deployment

### Security Checklist

- [ ] Regenerate Discord token (don't use dev token in production)
- [ ] Use strong MongoDB credentials
- [ ] Never commit `.env` or `config.yaml` to version control
- [ ] Set `track_command_args: false` if handling sensitive data
- [ ] Enable only required Discord intents
- [ ] Set appropriate owner IDs
- [ ] Use `dev_guild_id: null` for global command deployment

### Performance Tips

- Increase `mongodb.pool_size` for high-traffic bots (10-50)
- Set `aggregate_metrics_interval` to 600+ seconds (10 min)
- Monitor memory usage with `/metrics` command
- Use MongoDB Atlas for automatic backups and scaling

### Monitoring

The bot provides comprehensive observability:

1. **Command Tracking**: Every command is logged with execution time
2. **Error Tracking**: All errors get unique reference codes
3. **Metrics**: Periodic snapshots of performance data

Use the `/errors` and `/metrics` commands to view real-time data.

## 🔧 Troubleshooting

<details>
<summary><b>Bot won't start</b></summary>

- **Check MongoDB**: Ensure MongoDB is running
- **Verify credentials**: Check your `.env` file
- **Check config.yaml**: Ensure application_id is correct
- **Check logs**: Look for error messages in the console

</details>

<details>
<summary><b>Commands not showing</b></summary>

- **Check intents**: Ensure required intents are enabled
- **Sync commands**: Use `/sync` or restart the bot
- **Check dev_guild_id**: Set to your test server for instant updates
- **Wait**: Global commands can take up to 1 hour to sync

</details>

<details>
<summary><b>Permission errors</b></summary>

- **Bot role position**: Ensure bot's role is above target roles
- **Bot permissions**: Grant required permissions in server settings
- **Command permissions**: Check Discord's command permissions settings

</details>

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Format code: `black .`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 💬 Support

- **Documentation**: [Discord.py Docs](https://discordpy.readthedocs.io/)
- **Issues**: [Open an issue on GitHub](https://github.com/Lagden-Development/rickbot/issues)
- **Discord**: [Join our support server](https://discord.gg/zXumZ5jsBF)

## 🙏 Credits

Built with:
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [motor](https://github.com/mongodb/motor) - Async MongoDB driver
- [pydantic](https://github.com/pydantic/pydantic) - Data validation
- [termcolor](https://github.com/termcolor/termcolor) - Colored terminal output

---

<div align="center">

Made with ❤️ by **Lagden Development**

[⬆ Back to Top](#-rickbot-20)

</div>
