"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This cog provides commands to get information about the bot, and it is part of the RickBot default cog set.
"""

# Python Standard Library
# ------------------------
from datetime import (
    datetime,
)  # Used for parsing and formatting date and time information

# Third Party Libraries
# ---------------------
from discord_timestamps import (
    format_timestamp,
    TimestampType,
)  # Helps format timestamps for Discord messages
from discord.ext import commands  # Used for defining Discord bot commands and cogs
import discord  # Core library for interacting with Discord's API
import requests  # Handles HTTP requests, used here for interacting with the GitHub API

# Internal Modules
# ----------------
from helpers.colors import (
    MAIN_EMBED_COLOR,
    ERROR_EMBED_COLOR,
)  # Predefined color constants for Discord embeds

# Config
# ------
from config import CONFIG  # Imports the bot's configuration settings


# Custom Exceptions
class InvalidGitHubURL(Exception):
    """
    Exception raised when an invalid GitHub URL is encountered.

    Attributes:
    message (str): The error message explaining the issue.
    """

    def __init__(self, message: str = "Invalid GitHub URL"):
        self.message = message
        super().__init__(self.message)


# Helper functions
def convert_repo_url_to_api(url: str) -> str:
    """
    Converts a GitHub repository URL into the corresponding GitHub API URL to retrieve commits.

    Args:
    url (str): The GitHub repository URL.

    Returns:
    str: The corresponding GitHub API URL for commits.

    Raises:
    ValueError: If the provided URL is invalid.
    """
    # Split the URL by slashes
    parts = url.rstrip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    # Extract the owner and repository name
    owner = parts[-2]
    repo = parts[-1]

    # Construct the API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    return api_url


# Cog
class RickBot_BotInfoCommands(commands.Cog):
    """
    Cog for RickBot that provides commands to retrieve information about the bot, including recent GitHub updates.

    Attributes:
    bot (commands.Bot): The instance of the bot.
    GITHUB_REPO (str): The GitHub repository URL configured for the bot.
    GITHUB_API (str): The GitHub API URL derived from the repository URL.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.GITHUB_REPO = CONFIG["REPO"]["url"]

        if self.GITHUB_REPO is not None:
            self.GITHUB_API = convert_repo_url_to_api(self.GITHUB_REPO)
        else:
            self.GITHUB_API = None

    @commands.command(name="updates")
    async def _updates(self, ctx: commands.Context):
        """
        Check GitHub for the latest commits and provide details about the last 5 commits.

        Args:
        ctx (commands.Context): The command context.
        """
        if self.GITHUB_API in [None, ""]:
            embed = discord.Embed(
                title="Sorry!",
                description="This command is disabled.",
                color=ERROR_EMBED_COLOR,
            )

            await ctx.message.reply(embed=embed, mention_author=False)
            return

        try:
            response = requests.get(self.GITHUB_API)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            if not isinstance(data, list):
                raise ValueError("Unexpected data format received from GitHub API")

            # Sort the commits by date (newest first)
            sorted_commits = sorted(
                data,
                key=lambda x: datetime.strptime(
                    x["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
                ),
                reverse=True,
            )

            # Extract required information
            commit_list = []
            for commit in sorted_commits[:5]:  # Only process the latest 5 commits
                author_data = commit.get("author")
                commit_info = {
                    "sha": commit["sha"],
                    "id": commit["sha"][:7],
                    "date": commit["commit"]["author"]["date"],
                    "author": commit["commit"]["author"]["name"],
                    "author_html_url": (
                        author_data["html_url"] if author_data else "N/A"
                    ),
                    "email": commit["commit"]["author"]["email"],
                    "short_message": commit["commit"]["message"].split("\n")[0],
                    "full_message": commit["commit"]["message"],
                    "url": commit["url"],
                    "html_url": commit["html_url"],
                }
                commit_list.append(commit_info)

            # Create the embed
            desc = "Here are the latest updates to the bot:\n\n"

            for commit in commit_list:
                date = datetime.strptime(commit["date"], "%Y-%m-%dT%H:%M:%SZ")

                author_link = (
                    f"[{commit['author'].split(' ')[0]}]({commit['author_html_url']})"
                    if commit["author_html_url"] != "N/A"
                    else commit["author"].split(" ")[0]
                )
                desc += f"**[`{commit['id']}`]({commit['html_url']})** - {format_timestamp(date, TimestampType.RELATIVE)} by {author_link}\n{commit['short_message']}\n\n"

            embed = discord.Embed(
                title="Latest Updates",
                description=desc,
                color=MAIN_EMBED_COLOR,
            )

            embed.set_footer(text="RickBot is a project by lagden.dev.")

            await ctx.message.reply(embed=embed, mention_author=False)

        except requests.exceptions.RequestException as e:
            # Handle specific request errors like timeouts, connection errors, etc.
            embed = discord.Embed(
                title="Error",
                description="I'm sorry, there was an error fetching the latest commits. Please try again later.\nIf the problem persists, please contact the bot owner.",
                color=ERROR_EMBED_COLOR,
            )

            await ctx.message.reply(embed=embed, mention_author=False)

        except ValueError as e:
            # Handle JSON decoding errors or any other data format issues
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=ERROR_EMBED_COLOR,
            )

            await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command(name="ping")
    async def _ping(self, ctx: commands.Context):
        """
        Check the bot's latency.

        Args:
        ctx (commands.Context): The command context.
        """
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            color=MAIN_EMBED_COLOR,
        )

        await ctx.message.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    """
    Setup function to add this cog to the bot.

    Args:
    bot (commands.Bot): The instance of the bot.
    """
    await bot.add_cog(RickBot_BotInfoCommands(bot))
