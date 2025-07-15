# cogs/rickbot/cmds_botinfo.py
"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot Bot Info Chat Commands Cog

This module provides a cog with commands to retrieve information about the bot,
including recent GitHub updates, latency checks, and general bot information.
It is part of the RickBot default cog set.
"""

from typing import Optional
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

    This cog includes functionality to check for updates from the bot's GitHub repository,
    ping the bot to check its latency, and get general bot information.

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
        self.github_repo = CONFIG["REPO"].get("url", "").strip()
        self.github_api = (
            convert_repo_url_to_api(self.github_repo) if self.github_repo else None
        )

    async def create_error_embed(self, title: str, description: str) -> discord.Embed:
        """
        Create a standardized error embed message.

        Args:
            title (str): The title for the error embed.
            description (str): The description/message for the error embed.

        Returns:
            discord.Embed: The formatted error embed.
        """
        embed = discord.Embed(
            title=title, description=description, color=ERROR_EMBED_COLOR
        )
        embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")
        return embed

    @commands.command(name="updates", help="Check GitHub for the latest commits")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def _updates(self, ctx: commands.Context) -> None:
        """
        Retrieve and display the latest commits from the bot's GitHub repository.

        This command fetches information about the last 5 commits from the configured
        GitHub repository and presents them in an embed. If the GitHub repository
        is not configured, it informs the user that the command is disabled.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        try:
            if not self.github_repo:
                embed = await self.create_error_embed(
                    "Sorry!", "The updates command is currently disabled."
                )
            else:
                embed = get_github_updates(self.github_repo)

            await ctx.reply(embed=embed, mention_author=False)

        except Exception as e:
            error_embed = await self.create_error_embed(
                "Error!", f"Failed to fetch updates: {str(e)}"
            )
            await ctx.reply(embed=error_embed, mention_author=False)

    @commands.command(name="ping", help="Check the bot's latency")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _ping(self, ctx: commands.Context) -> None:
        """
        Check and display the bot's current latency.

        This command calculates the bot's latency to the Discord server
        and presents it in milliseconds within an embed.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        try:
            latency = round(self.bot.latency * 1000)
            embed = discord.Embed(
                title="Pong!",
                description=f"🏓 Latency: {latency}ms",
                color=MAIN_EMBED_COLOR,
            )
            embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")
            await ctx.reply(embed=embed, mention_author=False)

        except Exception as e:
            error_embed = await self.create_error_embed(
                "Error!", f"Failed to check latency: {str(e)}"
            )
            await ctx.reply(embed=error_embed, mention_author=False)

    @commands.command(name="info", help="Get information about the bot")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def _info(self, ctx: commands.Context) -> None:
        """
        Provide general information about the bot.

        This command displays various details about the bot, including its version,
        developer information, and GitHub repository link (if available).

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        try:
            embed = discord.Embed(
                title="RickBot Information",
                description="RickBot is a versatile Discord bot developed by Lagden Development.",
                color=MAIN_EMBED_COLOR,
            )
            embed.add_field(
                name="Version",
                value=CONFIG["VERSION"].get("version", "Unknown"),
                inline=True,
            )
            embed.add_field(
                name="Developer",
                value=f"<@{CONFIG['MAIN'].get('dev', 'Unknown')}>",
                inline=True,
            )
            embed.add_field(
                name="GitHub", value=self.github_repo or "Not available", inline=False
            )
            embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")
            await ctx.reply(embed=embed, mention_author=False)

        except Exception as e:
            error_embed = await self.create_error_embed(
                "Error!", f"Failed to fetch bot info: {str(e)}"
            )
            await ctx.reply(embed=error_embed, mention_author=False)

    @_updates.error
    @_ping.error
    @_info.error
    async def command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Handle errors that occur in commands.

        Args:
            ctx (commands.Context): The context in which the error occurred.
            error (Exception): The error that occurred.
        """
        if isinstance(error, commands.CommandOnCooldown):
            embed = await self.create_error_embed(
                "Slow down!",
                f"Please wait {error.retry_after:.1f}s before using this command again.",
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = await self.create_error_embed(
                "Error!", "An unexpected error occurred. Please try again later."
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
