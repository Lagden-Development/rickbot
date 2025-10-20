"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Permission Checks

Custom check decorators for slash commands.
"""

import discord
from discord import app_commands
from typing import Union


def is_owner():
    """
    Check if user is a bot owner (from config).

    Usage:
        @app_commands.command()
        @is_owner()
        async def admin_command(self, interaction):
            ...
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        # Access bot config
        bot = interaction.client
        owner_ids = bot.config.bot.owner_ids

        if interaction.user.id in owner_ids:
            return True

        await interaction.response.send_message(
            "❌ This command is owner-only!", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def has_any_role(*role_ids: int):
    """
    Check if user has any of the specified roles.

    Args:
        *role_ids: Role IDs to check

    Usage:
        @app_commands.command()
        @has_any_role(123456789, 987654321)
        async def mod_command(self, interaction):
            ...
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "❌ This command can only be used in a server!", ephemeral=True
            )
            return False

        user_role_ids = [role.id for role in interaction.user.roles]
        if any(role_id in user_role_ids for role_id in role_ids):
            return True

        await interaction.response.send_message(
            "❌ You don't have the required role to use this command!", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def guild_only():
    """
    Check if command is used in a guild (not DMs).

    Usage:
        @app_commands.command()
        @guild_only()
        async def server_command(self, interaction):
            ...
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is not None:
            return True

        await interaction.response.send_message(
            "❌ This command can only be used in a server!", ephemeral=True
        )
        return False

    return app_commands.check(predicate)
