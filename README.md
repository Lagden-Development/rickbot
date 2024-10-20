![GitHub Release](https://img.shields.io/github/v/release/Lagden-Development/rickbot)
![GitHub branch check runs](https://img.shields.io/github/check-runs/Lagden-Development/rickbot/main)
![Codacy Badge](https://app.codacy.com/project/badge/Grade/d20be7f7ddcf429bb59329b97cee6903)

# RickBot - Advanced Discord.py Framework

**Note:** This documentation is yet to be updated for RickBot 1.2.1.

RickBot is an advanced framework designed for building complex (or simple) Discord bots quickly and efficiently using discord.py.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
   - [Config Files Overview](#config-files-overview)
   - [Example `config.json`](#example-configjson)
5. [Project Structure](#project-structure)
6. [Usage](#usage)
7. [Creating Custom Cogs](#creating-custom-cogs)
   - [Example Cog](#example-cog)
8. [Database Integration](#database-integration)
   - [Example MongoDB Usage](#example-mongodb-usage)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

- [Getting Started](#getting-started)
- [Making Changes](#making-changes)
- [Testing Your Changes](#testing-your-changes)
- [Submitting Changes](#submitting-changes)
- [Contribution Guidelines](#contribution-guidelines)

11. [Support](#support)

- [How to Get Support](#how-to-get-support)

12. [License](#license)

## Introduction

RickBot is designed to help developers build scalable and maintainable Discord bots with ease. Using the discord.py library, RickBot provides a structured and modular approach to bot development, making it simple to extend functionality as your bot grows.

## Features

- **Modular Design:** Easily add or remove features through cogs.
- **Database Integration:** MongoDB is supported for robust and flexible data storage.
- **Highly Configurable:** Extensive options for fine-tuning bot behavior.
- **Extensible:** Quickly add custom commands and events.

## Installation

### Prerequisites

Ensure the following software is installed on your system:

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package installer (typically included with Python)
- **git**: [Download Git](https://git-scm.com/)
- **MongoDB**: [MongoDB Setup Guide](https://www.mongodb.com/) | [Free MongoDB Deployment](https://www.mongodb.com/atlas)

### Installation Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/zachlagden/rickbot
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd rickbot
   ```

3. **Install Required Packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Config Files Overview

- `config.json`: Holds the core bot configuration.
- `customconfig.json`: Optional file for additional custom settings.

> **Note:** `config.py` is not a configuration file itself. It ensures that `config.json` and `customconfig.json` are properly loaded into the project.

### Example `config.json`

```json
{
  "mode": "dev",
  "devs": [123456789],
  "bot": {
    "token": "BOT TOKEN",
    "prefix": "!",
    "status": {
      "type": "playing",
      "message": "a game"
    }
  },
  "behaviour": {
    "continue_to_load_cogs_after_failure": false
  },
  "mongo": {
    "uri": "mongodb uri",
    "bot_specific_db": "bot"
  }
}
```

## Project Structure

- **`app.py`**: Main entry point for running the bot.
- **`cogs/`**: Directory for bot functionality modules (cogs).
- **`helpers/`**: Utility functions and helper scripts.
- **`rickbot/`**: Core framework files for RickBot.
- **`config.json`**: Primary configuration file.
- **`customconfig.json`**: Optional file for additional custom settings.

## Usage

To start the bot, run the following command:

```bash
python app.py
```

## Creating Custom Cogs

Cogs are modular extensions used to add functionality to your bot. They should be placed in the `cogs/<category>/` directory, where additional folders separate cog categories. To maintain optimal organization, RickBot encourages using one cog per command.

### Example Cog

```python
import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello, world!")

def setup(bot):
    bot.add_cog(ExampleCog(bot))
```

## Database Integration

RickBot integrates with MongoDB for data storage. Ensure your MongoDB URI is correctly set in the `config.json` file. The `db.py` file serves as a convenient base for managing database connections and collections, but feel free to customize it to meet your specific requirements.

### Example MongoDB Usage

```python
from pymongo import MongoClient
from config import CONFIG

client = MongoClient(CONFIG['mongo']['uri'])
db = client['rickbot']
collection = db['example']
```

## Troubleshooting

- **Installation Issues:** Ensure all prerequisites are correctly installed, and verify your environment variables.
- **Bot Not Responding:** Confirm that the bot token is valid and the bot has appropriate permissions.
- **Database Errors:** Verify your MongoDB URI and ensure that MongoDB is running.

## Contributing

Contributions are welcome! Whether you're fixing bugs, adding features, or improving documentation, your contributions help improve RickBot.

### Getting Started

1. **Fork the Repository:** Click the "Fork" button on the repository page.
2. **Clone Your Fork:** Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Lagden-Development/rickbot.git
   ```

3. **Create a Branch:** Always create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. **Commit Messages:** Write clear and concise commit messages. Use this format:

   ```text
   [Component] Brief description of changes
   ```

   Example:

   ```text
   [Cog] Added command to fetch weather updates
   ```

2. **Code Style:** Maintain the existing code style. Use consistent indentation and document complex logic with comments.
3. **Documentation:** Update relevant documentation (including the README) to reflect your changes. Add docstrings where appropriate.

### Testing Your Changes

1. **Run Tests:** Test your changes to ensure they work as expected.
2. **Lint Your Code:** Run a linter to check for code style issues:

   ```bash
   flake8 your_file.py
   ```

### Submitting Changes

1. **Push to Your Fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request:** Open a pull request on the original repository with a detailed description of your changes and any issues it addresses.

### Contribution Guidelines

- **Bug Fixes:** Reference the issue number in your commit messages and pull request description.
- **New Features:** Clearly explain the new feature and its value.
- **Documentation:** Ensure all new features are documented appropriately.

## Support

If you need help or have questions, we’re here to assist you. However, please keep the following in mind:

- **RickBot Issues:** We provide support for any bugs, feature requests, or general questions related to RickBot. Join our [Discord Server](https://discord.gg/zXumZ5jsBF) or get in contact via [Email](mailto:contact@lagden.dev).
- **discord.py Issues:** For issues related specifically to discord.py, please refer to the [discord.py documentation](https://discordpy.readthedocs.io/en/stable/) or join the [discord.py support server](https://discord.gg/dpy).

### How to Get Support

1. **Check Existing Issues:** Search the [issue tracker](https://github.com/zachlagden/rickbot/issues) for similar problems before posting a new issue.
2. **Create a New Issue:** If no solution is found, create a new issue and provide as much detail as possible, including steps to reproduce and any error messages.
3. **Submit a Pull Request:** If you have a solution for the issue, feel free to submit a pull request.

## License

This project is licensed under a non-commercial open-source license. View the full license [here](https://github.com/Lagden-Development/.github/blob/main/LICENSE).
