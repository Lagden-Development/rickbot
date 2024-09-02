"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This cog provides utility commands for RickBot, allowing the bot owner to execute, evaluate, and manage code and commands directly through Discord. 
It also includes error handling and a test error command.
"""

# Python Standard Library
# ------------------------
import subprocess  # Used for running shell commands from within Python code

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
from helpers.errors import handle_error  # Custom error handling function

# Config
# ------
from config import CONFIG  # Imports the bot's configuration settings


# Helper Functions
def botownercheck(ctx: commands.Context) -> bool:
    """
    Check if the user is the bot owner.

    Args:
    ctx (commands.Context): The command context.

    Returns:
    bool: True if the user is the bot owner, False otherwise.
    """
    return ctx.author.id == int(CONFIG["MAIN"]["dev"])


# Cog
class RickBot_BotUtilsCommands(commands.Cog):
    """
    Cog for RickBot that provides utility commands for the bot owner.

    This includes commands for evaluating code, executing code, running shell commands, and a command for testing error handling.

    Attributes:
    bot (commands.Bot): The instance of the bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.check(botownercheck)
    async def eval(self, ctx: commands.Context, *, code: str):
        """
        Evaluate a string of Python code.

        Args:
        ctx (commands.Context): The command context.
        code (str): The Python code to evaluate.
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
    async def eval_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Error handler for the eval command.

        Args:
        ctx (commands.Context): The command context.
        error (commands.CommandError): The exception raised during command execution.
        """
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
        Execute a string of Python code.

        Args:
        ctx (commands.Context): The command context.
        code (str): The Python code to execute.
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
    async def exec_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Error handler for the exec command.

        Args:
        ctx (commands.Context): The command context.
        error (commands.CommandError): The exception raised during command execution.
        """
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
        Run a shell command.

        Args:
        ctx (commands.Context): The command context.
        cmd (str): The shell command to run.
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
    async def cmd_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Error handler for the cmd command.

        Args:
        ctx (commands.Context): The command context.
        error (commands.CommandError): The exception raised during command execution.
        """
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
        Trigger an error for testing purposes.

        Args:
        ctx (commands.Context): The command context.
        """
        await ctx.message.add_reaction("👌")
        raise Exception("Test error.")


async def setup(bot: commands.Bot):
    """
    Setup function to add this cog to the bot.

    Args:
    bot (commands.Bot): The instance of the bot.
    """
    await bot.add_cog(RickBot_BotUtilsCommands(bot))
