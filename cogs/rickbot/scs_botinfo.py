# cogs/rickbot/scs_botinfo.py
"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot Bot Info Slash Commands Cog

This cog provides slash commands to retrieve information about the bot, which is part 
of the RickBot default cog set. It includes functionality to check for updates, 
ping the bot, and get general bot information.
"""

from typing import Optional
from discord.ext import commands
from discord import app_commands, Interaction, Embed

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR
from cogs.rickbot.helpers.github_updates import (
    convert_repo_url_to_api,
    get_github_updates,
)
from config import CONFIG


@app_commands.guild_only()
class RickBot_BotInfo_SlashCommands(commands.Cog):
    """
    A cog that provides slash commands for retrieving bot information.

    This cog includes commands to check for updates from the bot's GitHub repository,
    ping the bot to check its latency, and retrieve general information about the bot.

    Attributes:
        bot (commands.Bot): The instance of the bot.
        github_repo (str): The GitHub repository URL configured for the bot.
        github_api (str): The GitHub API URL derived from the repository URL.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the RickBot_BotInfo_SlashCommands cog.

        Args:
            bot (commands.Bot): The instance of the bot.
        """
        self.bot = bot
        self.github_repo = CONFIG["REPO"].get("url", "").strip()
        self.github_api = (
            convert_repo_url_to_api(self.github_repo) if self.github_repo else None
        )

    async def create_error_embed(self, title: str, description: str) -> Embed:
        """
        Create a standardized error embed message.

        Args:
            title (str): The title for the error embed.
            description (str): The description/message for the error embed.

        Returns:
            Embed: The formatted error embed.
        """
        embed = Embed(title=title, description=description, color=ERROR_EMBED_COLOR)
        embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")
        return embed

    @app_commands.command(
        name="updates", description="Check GitHub for the latest commits."
    )
    @app_commands.checks.cooldown(1, 30.0)
    async def updates(self, interaction: Interaction) -> None:
        """
        Check GitHub for the latest commits and provide information about recent updates.

        This command fetches the last 5 commits from the bot's GitHub repository and
        displays them along with other relevant information. If the GitHub repository
        is not configured, it informs the user that the command is disabled.

        Args:
            interaction (Interaction): The interaction that triggered this command.
        """
        try:
            if not self.github_repo:
                embed = await self.create_error_embed(
                    "Sorry!", "The updates command is currently disabled."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            embed = get_github_updates(self.github_repo)
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            error_embed = await self.create_error_embed(
                "Error!", f"Failed to fetch updates: {str(e)}"
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="ping", description="Check the bot's latency.")
    @app_commands.checks.cooldown(1, 10.0)
    async def ping(self, interaction: Interaction) -> None:
        """
        Check and display the bot's current latency.

        This command calculates the bot's latency to the Discord server and
        presents it in milliseconds.

        Args:
            interaction (Interaction): The interaction that triggered this command.
        """
        try:
            latency = round(self.bot.latency * 1000)
            embed = Embed(
                title="Pong!",
                description=f"🏓 Latency: {latency}ms",
                color=MAIN_EMBED_COLOR,
            )
            embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            error_embed = await self.create_error_embed(
                "Error!", f"Failed to check latency: {str(e)}"
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="info", description="Get information about the bot.")
    @app_commands.checks.cooldown(1, 30.0)
    async def info(self, interaction: Interaction) -> None:
        """
        Provide general information about the bot.

        This command displays various details about the bot, including its version,
        developer information, and GitHub repository link (if available).

        Args:
            interaction (Interaction): The interaction that triggered this command.
        """
        try:
            embed = Embed(
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
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            error_embed = await self.create_error_embed(
                "Error!", f"Failed to fetch bot info: {str(e)}"
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    async def cog_app_command_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:
        """
        Handle errors that occur in slash commands.

        Args:
            interaction (Interaction): The interaction where the error occurred.
            error (app_commands.AppCommandError): The error that occurred.
        """
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = await self.create_error_embed(
                "Slow down!",
                f"Please wait {error.retry_after:.1f}s before using this command again.",
            )
        else:
            embed = await self.create_error_embed(
                "Error!", "An unexpected error occurred. Please try again later."
            )

        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """
    Set up the RickBot_BotInfo_SlashCommands cog.

    This function is called by Discord.py when adding the cog to the bot.

    Args:
        bot (commands.Bot): The instance of the bot.

    Returns:
        None
    """
    await bot.add_cog(RickBot_BotInfo_SlashCommands(bot))
