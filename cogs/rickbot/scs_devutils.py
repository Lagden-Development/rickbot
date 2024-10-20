"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot Developer Utilities Slash Commands Cog

This module provides a set of utility commands for bot developers, including code evaluation,
command execution, error testing, and bot management. These commands are restricted to authorized
bot developers for security purposes.
"""

import os
import subprocess
import asyncio
from typing import Any, Callable, NoReturn

from discord.ext import commands
from discord import app_commands, Interaction, Embed

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR
from helpers.errors import handle_error
from config import CONFIG


def botdevcheck(interaction: Interaction) -> bool:
    """
    Check if the user is an authorized bot developer.

    Args:
        interaction (Interaction): The Discord interaction object.

    Returns:
        bool: True if the user is a bot developer, False otherwise.
    """
    return interaction.user.id == int(CONFIG["MAIN"]["dev"])


class RickBot_BotDevUtils_SlashCommands(commands.Cog):
    """
    A cog containing utility commands for bot developers.

    This cog provides slash commands for evaluating Python code, executing system commands,
    testing error handling, and managing the bot. All commands are restricted to authorized
    bot developers.

    Attributes:
        bot (commands.Bot): The bot instance.
        dev_mode (bool): Indicates whether the bot is running in development mode.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the RickBot_BotDevUtils_SlashCommands cog.

        Args:
            bot (commands.Bot): The bot instance to which this cog is attached.
        """
        self.bot = bot
        self.dev_mode = CONFIG["MAIN"]["mode"] == "dev"

    async def _send_embed(
        self, interaction: Interaction, title: str, description: str, color: int
    ) -> NoReturn:
        """
        Send a formatted Discord embed as a response to an interaction.

        Args:
            interaction (Interaction): The Discord interaction to respond to.
            title (str): The title of the embed.
            description (str): The description/content of the embed.
            color (int): The color of the embed.
        """
        embed = Embed(title=title, description=description, color=color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

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

    @app_commands.command(
        name="eval", description="Evaluate Python code. Restricted to bot developers."
    )
    @app_commands.check(botdevcheck)
    async def eval(self, interaction: Interaction, *, code: str) -> NoReturn:
        """
        Evaluate Python code and return the result.

        This command allows bot developers to execute Python expressions and view the output.

        Args:
            interaction (Interaction): The Discord interaction object.
            code (str): The Python code to evaluate.
        """
        str_output = await self._execute_code(code, eval)
        await self._send_embed(
            interaction, "Eval", f"```py\n{str_output}```", MAIN_EMBED_COLOR
        )

    @app_commands.command(
        name="exec", description="Execute Python code. Restricted to bot developers."
    )
    @app_commands.check(botdevcheck)
    async def exec(self, interaction: Interaction, *, code: str) -> NoReturn:
        """
        Execute Python code.

        This command allows bot developers to execute Python statements and view the output.

        Args:
            interaction (Interaction): The Discord interaction object.
            code (str): The Python code to execute.
        """
        str_output = await self._execute_code(code, exec)
        await self._send_embed(
            interaction, "Exec", f"```py\n{str_output}```", MAIN_EMBED_COLOR
        )

    @app_commands.command(
        name="cmd", description="Run a system command. Restricted to bot developers."
    )
    @app_commands.check(botdevcheck)
    async def cmd(self, interaction: Interaction, *, cmd: str) -> NoReturn:
        """
        Run a system command and return the output.

        This command allows bot developers to execute system commands and view the output.

        Args:
            interaction (Interaction): The Discord interaction object.
            cmd (str): The system command to execute.
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
        await self._send_embed(
            interaction, "Command", f"```{str_output}```", MAIN_EMBED_COLOR
        )

    @app_commands.command(
        name="testerror",
        description="Test error handling. Restricted to bot developers.",
    )
    @app_commands.check(botdevcheck)
    async def testerror(self, interaction: Interaction) -> NoReturn:
        """
        Raise a test error to verify error handling.

        This command intentionally raises an exception to test the bot's error handling mechanisms.

        Args:
            interaction (Interaction): The Discord interaction object.
        """
        await interaction.response.send_message(
            "Raising a test error...", ephemeral=True
        )
        raise Exception("Test error raised.")

    @app_commands.command(
        name="restart", description="Restart the bot. Restricted to bot developers."
    )
    @app_commands.check(botdevcheck)
    async def restart(self, interaction: Interaction) -> None:
        """
        Restart the bot using the configured Linux service.

        This command attempts to restart the bot by restarting its associated Linux service.
        The service name must be configured in the bot's configuration file.

        Args:
            interaction (Interaction): The Discord interaction object.
        """
        service_name = CONFIG["ADVANCED"].get("linux_service_name")
        if not service_name:
            await interaction.response.send_message(
                "The Linux service name is not set in the config file.", ephemeral=True
            )
            return

        await interaction.response.send_message("Restarting the bot...", ephemeral=True)
        os.system(f"systemctl restart {service_name}")

    async def cog_app_command_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> NoReturn:
        """
        Handle errors for all commands in this cog.

        This method provides centralized error handling for all commands within the cog.
        It distinguishes between permission errors and other types of errors.

        Args:
            interaction (Interaction): The Discord interaction object.
            error (app_commands.AppCommandError): The error that occurred during command execution.
        """
        if isinstance(error, app_commands.CheckFailure):
            await self._send_embed(
                interaction,
                "Error",
                "Only the bot developer can run this command.",
                ERROR_EMBED_COLOR,
            )
        else:
            await handle_error(interaction, error)


async def setup(bot: commands.Bot) -> NoReturn:
    """
    Set up the RickBot_BotDevUtils_SlashCommands cog.

    This function is called by the bot to add the cog to its extension list.

    Args:
        bot (commands.Bot): The bot instance to which this cog will be added.
    """
    await bot.add_cog(RickBot_BotDevUtils_SlashCommands(bot))
