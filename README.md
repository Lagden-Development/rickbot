# Rickbot - Advanced discord.py Framework

Rickbot is an advanced framework for creating complex (or simple) Discord bots quickly and efficiently using discord.py.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Steps](#steps)
4. [Configuration](#configuration)
   - [Config Files](#config-files)
   - [Example `config.json`](#example-configjson)
5. [Project Structure](#project-structure)
6. [Usage](#usage)
7. [Creating Custom Cogs](#creating-custom-cogs)
   - [Example Cog](#example-cog)
8. [Database Integration](#database-integration)
   - [Example Usage](#example-usage)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
   - [Getting Started](#getting-started)
   - [Making Changes](#making-changes)
   - [Testing](#testing)
   - [Submitting Changes](#submitting-changes)
   - [Guidelines](#guidelines)
11. [Support](#support)
   - [How to Get Support](#how-to-get-support)
12. [License](#license)

## Introduction

Rickbot is designed to help you build scalable and maintainable Discord bots with ease. Utilizing the discord.py library, Rickbot offers a structured approach to bot development.

## Features

- **Modular Design:** Easily add or remove features with cogs.
- **Database Support:** Integrated with MongoDB for robust data handling.
- **Configurable:** Extensive configuration options for flexibility.
- **Extensible:** Create custom commands and events effortlessly.

## Installation

### Prerequisites

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package installer (usually comes with Python)
- **git**: [Download Git](https://git-scm.com/)
- **MongoDB**: [Get started with MongoDB](https://www.mongodb.com/) | [Create a free MongoDB deployment](https://www.mongodb.com/atlas)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/zachlagden/rickbot
   ```
2. Navigate to the project directory:
   ```bash
   cd rickbot
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Config Files

- `config.json`: Contains general bot settings.
- `customconfig.json`: For additional custom settings.

### Note
- `config.py` is not a configuration file itself. It serves to ensure that the actual configuration files (`config.json`, `customconfig.json`) exist and are properly imported into the project.

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
            "message": "a game",
        },
    },
    "behaviour": {
        "continue_to_load_cogs_after_failure": false,
    },
    "mongo": {
        "uri": "mongodb uri",
        "bot_specific_db": "bot",
    },
}
```

## Project Structure

- `app.py`: The main entry point for the bot.
- `cogs/`: Directory for cog modules.
- `helpers/`: Utility functions and helpers.
- `rickbot/`: Core framework files.
- `config.json`: General configuration file.
- `customconfig.json`: Custom settings.

## Usage

Start the bot with:
```bash
python app.py
```

## Creating Custom Cogs

Cogs are modular extensions that add functionality to your bot. Create new cogs in the `cogs/<category>/` directory. Within the `cogs` folder, additional folders are used to separate categories of cogs. In RickBot, we aim to use one cog per command for optimal organization, with separate folders for different categories.

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

Rickbot uses MongoDB for data storage. Ensure your MongoDB URI is correctly set in `config.json`.

Rickbot uses `db.py` to predefine the accessed databases and collections from MongoDB. You can customize these definitions or manually manage your database interactions. The structure in `db.py` provides a convenient starting point, ensuring consistent database connections and collections usage across the bot. If you have specific requirements or prefer a different setup, feel free to modify `db.py` or implement your own database management methods to suit your needs.

### Example Usage
```python
from pymongo import MongoClient
from config import CONFIG

client = MongoClient(CONFIG['mongo']['uri'])
db = client['rickbot']
collection = db['example']
```

## Troubleshooting

- **Installation Issues:** Ensure all prerequisites are installed and paths are correctly set.
- **Bot Not Responding:** Check token validity and bot permissions.
- **Database Errors:** Verify MongoDB URI and database status.

## Contributing

I welcome contributions of all kinds to improve Rickbot. Whether you're fixing bugs, adding new features, or improving documentation, your efforts are highly appreciated. Follow these guidelines to contribute effectively.

### Getting Started

1. **Fork the Repository**: Create a personal copy of the repository by clicking the "Fork" button.
2. **Clone Your Fork**: Clone the repository to your local machine using:
   ```bash
   git clone https://github.com/Lagden-Development/rickbot.git
   ```
3. **Create a Branch**: Always create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. **Write Clear Commit Messages**: Each commit message should clearly describe what changes were made and why. Follow the convention:
   ```text
   [Component] Description of changes
   ```
   For example:
   ```text
   [Cog] Add new command for weather updates
   ```
2. **Code Style**: Follow the existing code style. Use consistent indentation and comments to explain complex logic.
3. **Documentation**: Update the README and any relevant documentation to reflect your changes. Add docstrings to new functions and classes.

### Testing

1. **Test Your Changes**: Ensure your changes work as expected. Run existing tests and add new ones if necessary.
2. **Lint Your Code**: Use a linter to check for code style issues. For example:
   ```bash
   flake8 your_file.py
   ```

### Submitting Changes

1. **Push to Your Fork**: Push your changes to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```
2. **Create a Pull Request**: Navigate to the original repository and create a pull request from your forked repository. Provide a detailed description of your changes and the issue it resolves (if applicable).

### Review Process

1. **Respond to Feedback**: Be prepared to make changes based on feedback from the project maintainers. Engage in the discussion to clarify any questions.
2. **Continuous Improvement**: Keep your branch updated with the latest changes from the main repository to avoid merge conflicts.

### Guidelines

- **Bug Fixes**: Reference the issue number you are fixing in your commit messages and pull request description.
- **New Features**: Provide a clear explanation of the feature and why it is beneficial.
- **Documentation**: Ensure all new features and changes are documented. This includes updating code comments, docstrings, and the README.

## Support

If you encounter issues or have questions about Rickbot, we are here to help! However, please note the following guidelines for support:

- **Rickbot Issues**: I provide support for any issues related to Rickbot and its functionality. This includes bugs, feature requests, and general questions about how to use and extend Rickbot.
- **discord.py Issues**: I do not provide support for issues related to discord.py itself. For discord.py-specific problems, please refer to the [discord.py documentation](https://discordpy.readthedocs.io/en/stable/) or the [discord.py support server](https://discord.gg/dpy).

### How to Get Support

1. **Search Existing Issues**: Before creating a new issue, please check the [issue tracker](https://github.com/zachlagden/rickbot/issues) to see if your problem has already been reported or addressed.
2. **Create a New Issue**: If you don't find a solution, create a new issue in the [issue tracker](https://github.com/zachlagden/rickbot/issues). Provide as much detail as possible, including steps to reproduce the problem and any error messages.
3. **Pull Requests**: If you have a solution to an issue, feel free to submit a pull request. Please follow the contributing guidelines outlined in the [Contributing](#contributing) section.

## License

This project is licensed under the terms of the non-commercial open-source license. You can view the full license [here](https://github.com/zachlagden/zachlagden/blob/main/LICENCE).
