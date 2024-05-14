"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This cog counts the number of times a user has said the n-word in the server and provides a command to check the records,
as well as a leaderboard command that shows the top 10 users with the most n-word records.
"""

# Python standard library
import logging

# Third-party libraries
from discord.ext import commands
import discord

# Helper functions
from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR
from helpers.errors import handle_error

# Setup logger for this module
RICKLOG = logging.getLogger("rickbot")


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="example", aliases=["ex"], help="An example command.")
    async def example_command(self, ctx):
        embed = discord.Embed(
            title="Example Embed",
            description="This is an example embed.",
            color=MAIN_EMBED_COLOR,
        )

        await ctx.send(embed=embed)

    @example_command.error
    async def example_command_error(self, ctx, error):
        await handle_error(ctx, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCog(bot))
