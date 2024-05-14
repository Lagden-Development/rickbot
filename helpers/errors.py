"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is a helper for handling all discord.py related errors.
"""

# Import the required modules

# Third-party libraries
import discord
from discord.ext import commands

# Helper functions
from helpers.colors import ERROR_EMBED_COLOR


async def handle_error(ctx: commands.Context, error: Exception):
    """
    Handle errors that occur in the bot.

    :param ctx: The context in which the error occurred.
    :param error: The error that occurred.
    """

    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Error",
            description="Command not found.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error",
            description="Missing required argument.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Error",
            description="Bad argument.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error",
            description="You do not have the required permissions to run this command.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="Error",
            description="The bot does not have the required permissions to run this command.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Error",
            description=f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Error",
            description="You do not have the required roles to run this command.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    elif isinstance(error, commands.CommandInvokeError):
        embed = discord.Embed(
            title="Error",
            description="An error occurred while running the command.",
            color=ERROR_EMBED_COLOR,
        )
        await ctx.reply(embed=embed, mention_author=False)

    else:
        embed = discord.Embed(
            title="Error",
            description="An unknown error occurred; please contact staff.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)
