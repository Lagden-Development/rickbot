"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This cog counts the number of times a user has said the n-word in the server and provides a command to check the records,
as well as a leaderboard command that shows the top 10 users with the most n-word records.
"""

# Python standard library
import subprocess

# Third-party libraries
from discord.ext import commands
import discord

# Helper functions
from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR
from helpers.errors import handle_error

# Config
from config import CONFIG


class RickBot_BotUtilsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def botownercheck(ctx):
        return ctx.author.id in CONFIG["devs"]

    @commands.command()
    @commands.check(botownercheck)
    async def eval(self, ctx: commands.Context, *, code: str):
        """
        Evaluate code.
        """
        try:
            str_output = str(eval(code))
        except Exception as e:
            str_output = str(e)

        embed = discord.Embed(
            title="Eval", description=f"```py\n{str_output}```", color=MAIN_EMBED_COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)

    @eval.error
    async def eval_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="Error",
                description="Only the bot developer can run this command as it is dangerous.",
                color=ERROR_EMBED_COLOR,
            )
            await ctx.reply(embed=embed, mention_author=False)

        else:
            await handle_error(ctx, error)

    @commands.command()
    @commands.check(botownercheck)
    async def exec(self, ctx: commands.Context, *, code: str):
        """
        Execute code.
        """
        try:
            exec(code)
            str_output = "Executed successfully."
        except Exception as e:
            str_output = str(e)

        embed = discord.Embed(
            title="Exec", description=f"```py\n{str_output}```", color=MAIN_EMBED_COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)

    @exec.error
    async def exec_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="Error",
                description="Only the bot developer can run this command as it is dangerous.",
                color=ERROR_EMBED_COLOR,
            )
            await ctx.reply(embed=embed, mention_author=False)

        else:
            await handle_error(ctx, error)

    @commands.command()
    @commands.check(botownercheck)
    async def cmd(self, ctx: commands.Context, *, cmd: str):
        """
        Run a command.
        """

        try:
            str_output = subprocess.check_output(cmd, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            str_output = f"Error executing command: {e}"

        embed = discord.Embed(
            title="Command", description=f"```{str_output}```", color=MAIN_EMBED_COLOR
        )

        await ctx.reply(embed=embed, mention_author=False)

    @cmd.error
    async def cmd_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="Error",
                description="Only the bot developer can run this command as it is dangerous.",
                color=ERROR_EMBED_COLOR,
            )
            await ctx.reply(embed=embed, mention_author=False)

        else:
            await handle_error(ctx, error)

    @commands.command()
    @commands.check(botownercheck)
    async def testerror(self, ctx: commands.Context):
        """
        Cause an error.
        """

        await ctx.message.add_reaction("👌")

        raise Exception("Test error.")


async def setup(bot: commands.Bot):
    await bot.add_cog(RickBot_BotUtilsCommands(bot))
