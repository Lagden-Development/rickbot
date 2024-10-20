"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot Bot Utilities Chat Commands Cog

This module provides a set of utility commands for the bot owner, allowing direct interaction
with the bot's runtime environment through Discord. It includes functionality for code evaluation,
execution, shell command running, and error testing.
"""

import subprocess
import asyncio
from typing import Callable, NoReturn

from discord.ext import commands
import discord

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR
from helpers.errors import handle_error
from config import CONFIG


def botownercheck(ctx: commands.Context) -> bool:
    """
    Check if the user is the bot owner.

    Args:
        ctx (commands.Context): The command context containing information about the invoker.

    Returns:
        bool: True if the user is the bot owner, False otherwise.
    """
    return ctx.author.id == int(CONFIG["MAIN"]["dev"])


class RickBot_BotUtils_ChatCommands(commands.Cog):
    """
    A cog that provides utility commands for the bot owner.

    This cog includes commands for evaluating Python code, executing Python code,
    running shell commands, and testing error handling. All commands are restricted
    to the bot owner for security reasons.

    Attributes:
        bot (commands.Bot): The instance of the bot this cog is attached to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the RickBot_BotUtilsCommands cog.

        Args:
            bot (commands.Bot): The bot instance to which this cog is being added.
        """
        self.bot = bot

    async def _execute_code(self, code: str, exec_func: Callable) -> str:
        """
        Execute the provided code using the specified execution function.

        This method runs the code in a separate thread to prevent blocking the event loop.

        Args:
            code (str): The code to execute.
            exec_func (Callable): The function to use for execution (e.g., eval or exec).

        Returns:
            str: The output of the code execution or an error message.
        """
        try:
            output = await asyncio.to_thread(exec_func, code)
            return str(output) if output is not None else "Executed successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    async def _send_embed(
        self, ctx: commands.Context, title: str, description: str
    ) -> None:
        """
        Send a formatted Discord embed as a response to a command.

        Args:
            ctx (commands.Context): The context of the command invocation.
            title (str): The title of the embed.
            description (str): The description/content of the embed.
        """
        embed = discord.Embed(
            title=title, description=description, color=MAIN_EMBED_COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="eval")
    @commands.check(botownercheck)
    async def _eval(self, ctx: commands.Context, *, code: str) -> NoReturn:
        """
        Evaluate a string of Python code and return the result.

        This command allows the bot owner to execute Python expressions and view the output.

        Args:
            ctx (commands.Context): The context of the command invocation.
            code (str): The Python code to evaluate.
        """
        str_output = await self._execute_code(code, eval)
        await self._send_embed(ctx, "Eval", f"```py\n{str_output}```")

    @commands.command(name="exec")
    @commands.check(botownercheck)
    async def _exec(self, ctx: commands.Context, *, code: str) -> NoReturn:
        """
        Execute a string of Python code.

        This command allows the bot owner to execute Python statements and view the output.

        Args:
            ctx (commands.Context): The context of the command invocation.
            code (str): The Python code to execute.
        """
        str_output = await self._execute_code(code, exec)
        await self._send_embed(ctx, "Exec", f"```py\n{str_output}```")

    @commands.command(name="cmd")
    @commands.check(botownercheck)
    async def _cmd(self, ctx: commands.Context, *, cmd: str) -> NoReturn:
        """
        Run a shell command and return the output.

        This command allows the bot owner to execute system commands and view the output.

        Args:
            ctx (commands.Context): The context of the command invocation.
            cmd (str): The shell command to execute.
        """
        try:
            str_output = await asyncio.to_thread(
                subprocess.check_output,
                cmd,
                shell=True,
                text=True,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            str_output = f"Error executing command: {e.output}"
        await self._send_embed(ctx, "Command", f"```{str_output}```")

    @commands.command(name="testerror")
    @commands.check(botownercheck)
    async def _testerror(self, ctx: commands.Context) -> NoReturn:
        """
        Trigger an error for testing purposes.

        This command is used to test the error handling capabilities of the bot.

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        raise Exception("Test error.")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """
        Global error handler for all commands in this cog.

        This method catches any errors raised during command execution and handles them appropriately.

        Args:
            ctx (commands.Context): The context of the command invocation.
            error (commands.CommandError): The error that was raised during command execution.
        """
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="Error",
                description="Only the bot developer can run this command.",
                color=ERROR_EMBED_COLOR,
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            await handle_error(ctx, error)


async def setup(bot: commands.Bot) -> NoReturn:
    """
    Setup function to add this cog to the bot.

    This function is called by the bot when loading the cog.

    Args:
        bot (commands.Bot): The bot instance to which this cog is being added.
    """
    await bot.add_cog(RickBot_BotUtils_ChatCommands(bot))
