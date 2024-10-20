"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot Bot Info Chat Commands Cog

This module provides a cog with commands to retrieve information about the bot,
including recent GitHub updates and latency checks. It is part of the RickBot default cog set.
"""

from discord.ext import commands
import discord

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR
from cogs.rickbot.helpers.github_updates import (
    convert_repo_url_to_api,
    get_github_updates,
)
from config import CONFIG


class RickBot_BotInfoCommands(commands.Cog):
    """
    A cog that provides commands to retrieve information about the bot.

    This cog includes functionality to check for updates from the bot's GitHub repository
    and to ping the bot to check its latency.

    Attributes:
        bot (commands.Bot): The instance of the bot.
        github_repo (str): The GitHub repository URL configured for the bot.
        github_api (str): The GitHub API URL derived from the repository URL.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the RickBot_BotInfoCommands cog.

        Args:
            bot (commands.Bot): The instance of the bot to which this cog is being added.
        """
        self.bot = bot
        self.github_repo = CONFIG["REPO"]["url"]
        self.github_api = (
            convert_repo_url_to_api(self.github_repo) if self.github_repo else None
        )

    @commands.command(name="updates")
    async def _updates(self, ctx: commands.Context) -> None:
        """
        Retrieve and display the latest commits from the bot's GitHub repository.

        This command fetches information about the last 5 commits from the configured
        GitHub repository and presents them in an embed. If the GitHub repository
        is not configured, it informs the user that the command is disabled.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        if not self.github_repo or not self.github_repo.strip():
            embed = discord.Embed(
                title="Sorry!",
                description="This command is disabled.",
                color=ERROR_EMBED_COLOR,
            )
            embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")
        else:
            embed = get_github_updates(self.github_repo)

        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="ping")
    async def _ping(self, ctx: commands.Context) -> None:
        """
        Check and display the bot's current latency.

        This command calculates the bot's latency to the Discord server
        and presents it in milliseconds within an embed.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!", description=f"Latency: {latency}ms", color=MAIN_EMBED_COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot) -> None:
    """
    Set up the RickBot_BotInfoCommands cog.

    This function is called by Discord.py when adding the cog to the bot.

    Args:
        bot (commands.Bot): The bot instance to which this cog should be added.
    """
    await bot.add_cog(RickBot_BotInfoCommands(bot))
