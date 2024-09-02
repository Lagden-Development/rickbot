"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This cog provides commands to get information about the bot, which is a part of the RickBot default cog set.
"""

# Python Standard Library
# -----------------------
from typing import Union, NoReturn  # Used for type hinting

# Third Party Libraries
# ---------------------
from discord.ext import commands  # Used for defining Discord bot commands and cogs
from discord import app_commands  # Supports slash commands in Discord bots
import discord  # Core library for interacting with Discord's API

# Internal Modules
# ----------------
from helpers.colors import (
    MAIN_EMBED_COLOR,
    ERROR_EMBED_COLOR,
)  # Predefined color constants for Discord embeds
from cogs.rickbot.helpers.github_updates import (
    convert_repo_url_to_api,
    get_github_updates,
)  # Functions for interacting with the GitHub API

# Config
# ------
from config import CONFIG  # Imports the bot's configuration settings


# Cog
class RickBot_BotInfoSlashCommands(commands.Cog):
    """
    Cog for RickBot that provides slash commands to retrieve bot information.

    Attributes:
    bot (commands.Bot): The instance of the bot.
    GITHUB_REPO (str): The GitHub repository URL configured for the bot.
    GITHUB_API (str): The GitHub API URL derived from the repository URL.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.GITHUB_REPO = CONFIG["REPO"]["url"]

        # Run the function to cause an error, if the URL is invalid.
        convert_repo_url_to_api(self.GITHUB_REPO)

    @app_commands.command(
        name="updates", description="Check GitHub for the latest commits."
    )
    async def _updates(self, interaction: discord.Interaction) -> Union[NoReturn, None]:
        """
        Check GitHub for the latest commits, provides the last 5 along with other relevant information.
        """

        if self.GITHUB_REPO in [None, ""] or self.GITHUB_REPO.strip() == "":
            embed = discord.Embed(
                title="Sorry!",
                description="This command is disabled.",
                color=ERROR_EMBED_COLOR,
            )

            embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = get_github_updates(self.GITHUB_REPO)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def _ping(self, interaction: discord.Interaction) -> NoReturn:
        """
        Check the bot's latency.
        """
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            color=MAIN_EMBED_COLOR,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> NoReturn:
    """
    Setup function to add this cog to the bot.

    Args:
    bot (commands.Bot): The instance of the bot.
    """
    await bot.add_cog(RickBot_BotInfoSlashCommands(bot))
