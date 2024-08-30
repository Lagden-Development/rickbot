"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This cog provides commands to get information about the bot, this is a part of the RickBot default cog set.
"""

# Python standard library
from datetime import datetime

# Third-party libraries
from discord_timestamps import format_timestamp, TimestampType
from discord.ext import commands
from discord import app_commands
import discord
import requests

# Helper functions
from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR

# Config
from config import CONFIG


# Custom Exceptions
class InvalidGitHubURL(Exception):
    def __init__(self, message="Invalid GitHub URL"):
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
class RickBot_BotInfoSlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.GITHUB_REPO = CONFIG["repo"]["url"]

        if self.GITHUB_REPO is not None:
            self.GITHUB_API = convert_repo_url_to_api(self.GITHUB_REPO)
        else:
            self.GITHUB_API = None

    async def _send_embed(self, interaction, title, description, color):
        """Helper to send formatted Discord embeds."""
        embed = discord.Embed(title=title, description=description, color=color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="updates", description="Check GitHub for the latest commits."
    )
    async def _updates(self, interaction: discord.Interaction):
        """
        Check GitHub for the latest commits, provides the last 5 along with other relevant information.
        """

        if self.GITHUB_API is None:
            await self._send_embed(
                interaction,
                "Sorry!",
                "This command is disabled.",
                ERROR_EMBED_COLOR,
            )
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

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except requests.exceptions.RequestException as e:
            # Handle specific request errors like timeouts, connection errors, etc.
            await self._send_embed(
                interaction,
                "Error",
                "I'm sorry, there was an error fetching the latest commits. Please try again later.\nIf the problem persists, please contact the bot owner.",
                ERROR_EMBED_COLOR,
            )

        except ValueError as e:
            # Handle JSON decoding errors or any other data format issues
            await self._send_embed(
                interaction,
                "Error",
                str(e),
                ERROR_EMBED_COLOR,
            )

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def _ping(self, interaction: discord.Interaction):
        """
        Check the bot's latency.
        """
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            color=MAIN_EMBED_COLOR,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RickBot_BotInfoSlashCommands(bot))
