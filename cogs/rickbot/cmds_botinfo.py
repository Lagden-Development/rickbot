"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This cog provides commands to get information about the bot, and it is part of the RickBot default cog set.
"""

# Python Standard Library
# ------------------------
from typing import Union, NoReturn  # Used for type hinting

# Third Party Libraries
# ---------------------
from discord.ext import commands  # Used for defining Discord bot commands and cogs
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
class RickBot_BotInfoCommands(commands.Cog):
    """
    Cog for RickBot that provides commands to retrieve information about the bot, including recent GitHub updates.

    Attributes:
    bot (commands.Bot): The instance of the bot.
    GITHUB_REPO (str): The GitHub repository URL configured for the bot.
    GITHUB_API (str): The GitHub API URL derived from the repository URL.
    """

    def __init__(self, bot: commands.Bot) -> NoReturn:
        self.bot = bot

        self.GITHUB_REPO = CONFIG["REPO"]["url"]

        # Run the function to cause an error, if the URL is invalid.
        convert_repo_url_to_api(self.GITHUB_REPO)

    @commands.command(name="updates")
    async def _updates(self, ctx: commands.Context) -> Union[NoReturn, discord.Message]:
        """
        Check GitHub for the latest commits and provide details about the last 5 commits.

        Args:
        ctx (commands.Context): The command context.
        """
        if self.GITHUB_REPO in [None, ""] or self.GITHUB_REPO.strip() == "":
            embed = discord.Embed(
                title="Sorry!",
                description="This command is disabled.",
                color=ERROR_EMBED_COLOR,
            )

            embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")

            return await ctx.message.reply(embed=embed, mention_author=False)

        embed = get_github_updates(self.GITHUB_REPO)

        await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command(name="ping")
    async def _ping(self, ctx: commands.Context) -> NoReturn:
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


async def setup(bot: commands.Bot) -> NoReturn:
    """
    Setup function to add this cog to the bot.

    Args:
    bot (commands.Bot): The instance of the bot.
    """
    await bot.add_cog(RickBot_BotInfoCommands(bot))
