"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This cog provides utility commands for bot developers, such as evaluating code, executing commands, and testing errors.
These commands are restricted to bot developers only for security purposes.
"""

# Python Standard Library
# -----------------------
import os  # os is used for interacting with the operating system, particularly to execute system commands and manage processes.
import subprocess  # subprocess is used for running system commands and capturing their output.

# Third Party Libraries
# ---------------------
from discord.ext import (
    commands,
)  # commands is used for creating bot commands and cogs within the Discord bot framework.
from discord import (
    app_commands,
)  # app_commands is used for defining and managing slash commands in Discord.
import discord  # discord is the main library used for interacting with the Discord API.

# Internal Modules
# ----------------
from helpers.colors import (
    MAIN_EMBED_COLOR,
    ERROR_EMBED_COLOR,
)  # MAIN_EMBED_COLOR and ERROR_EMBED_COLOR are color codes used in embeds to maintain consistency in the bot's UI.
from helpers.errors import (
    handle_error,
)  # handle_error is a custom function used to manage errors within commands, providing a standardized response.

# Config
# ------
from config import (
    CONFIG,
)  # CONFIG is a configuration object used to access settings and constants across the bot.


# Helper Functions
def botownercheck(interaction: discord.Interaction) -> bool:
    """
    Checks if the user who invoked the command is a bot developer.

    Args:
        interaction (discord.Interaction): The interaction that triggered the command.

    Returns:
        bool: True if the user is a bot developer, False otherwise.
    """
    return interaction.user.id == int(CONFIG["MAIN"]["dev"])


# Cog
class RickBot_BotUtilsSlashCommands(commands.Cog):
    """
    This cog contains utility commands intended for bot developers, allowing them to evaluate Python code,
    execute system commands, and test error handling.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initializes the cog with the bot instance.

        Args:
            bot (commands.Bot): The instance of the bot to which this cog is added.
        """
        self.bot = bot

        # Check the mode in the config file
        if CONFIG["MAIN"]["mode"] != "dev":
            # Disable the commands if the bot is not in development mode
            pass

    async def _send_embed(
        self, interaction: discord.Interaction, title: str, description: str, color: int
    ) -> None:
        """
        Helper function to send formatted Discord embeds.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            title (str): The title of the embed.
            description (str): The description of the embed.
            color (int): The color of the embed.
        """
        embed = discord.Embed(title=title, description=description, color=color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="eval", description="Evaluate Python code. Restricted to bot developers."
    )
    @app_commands.check(botownercheck)
    async def eval(self, interaction: discord.Interaction, *, code: str) -> None:
        """
        Evaluates the provided Python code and returns the result.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            code (str): The Python code to evaluate.
        """
        try:
            # Evaluate the code and convert the output to a string
            str_output = str(eval(code))
        except Exception as e:
            # Capture and convert any exceptions to a string
            str_output = str(e)

        # Create and send an embed with the output
        await self._send_embed(
            interaction, "Eval", f"```py\n{str_output}```", MAIN_EMBED_COLOR
        )

    @eval.error
    async def eval_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """
        Handles errors for the eval command.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            error (commands.CommandError): The error that occurred.
        """
        if isinstance(error, app_commands.CheckFailure):
            # Notify the user that only bot developers can run this command
            await self._send_embed(
                interaction,
                "Error",
                "Only the bot developer can run this command.",
                ERROR_EMBED_COLOR,
            )
        else:
            # Handle other errors using the global error handler
            await handle_error(interaction, error)

    @app_commands.command(
        name="exec", description="Execute Python code. Restricted to bot developers."
    )
    @app_commands.check(botownercheck)
    async def exec(self, interaction: discord.Interaction, *, code: str) -> None:
        """
        Executes the provided Python code.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            code (str): The Python code to execute.
        """
        try:
            # Execute the code block
            exec(code)
            str_output = "Executed successfully."
        except Exception as e:
            # Capture and convert any exceptions to a string
            str_output = str(e)

        # Create and send an embed with the result
        await self._send_embed(
            interaction, "Exec", f"```py\n{str_output}```", MAIN_EMBED_COLOR
        )

    @exec.error
    async def exec_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """
        Handles errors for the exec command.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            error (commands.CommandError): The error that occurred.
        """
        if isinstance(error, app_commands.CheckFailure):
            # Notify the user that only bot developers can run this command
            await self._send_embed(
                interaction,
                "Error",
                "Only the bot developer can run this command.",
                ERROR_EMBED_COLOR,
            )
        else:
            # Handle other errors using the global error handler
            await handle_error(interaction, error)

    @app_commands.command(
        name="cmd", description="Run a system command. Restricted to bot developers."
    )
    @app_commands.check(botownercheck)
    async def cmd(self, interaction: discord.Interaction, *, cmd: str) -> None:
        """
        Runs the specified system command and returns the output.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            cmd (str): The system command to run.
        """
        try:
            # Run the system command and capture the output
            str_output = subprocess.check_output(cmd, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            # Capture and convert any errors during execution to a string
            str_output = f"Error executing command: {e}"

        # Create and send an embed with the command output
        await self._send_embed(
            interaction, "Command", f"```{str_output}```", MAIN_EMBED_COLOR
        )

    @cmd.error
    async def cmd_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """
        Handles errors for the cmd command.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            error (commands.CommandError): The error that occurred.
        """
        if isinstance(error, app_commands.CheckFailure):
            # Notify the user that only bot developers can run this command
            await self._send_embed(
                interaction,
                "Error",
                "Only the bot developer can run this command.",
                ERROR_EMBED_COLOR,
            )
        else:
            # Handle other errors using the global error handler
            await handle_error(interaction, error)

    @app_commands.command(
        name="testerror",
        description="Test error handling. Restricted to bot developers.",
    )
    @app_commands.check(botownercheck)
    async def testerror(self, interaction: discord.Interaction) -> None:
        """
        Raises a test error to verify error handling.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
        """
        # React to the interaction message (This will raise an error since it is a slash command)
        await interaction.response.send_message(
            "Raising a test error...", ephemeral=True
        )
        raise Exception("Test error raised.")

    @testerror.error
    async def testerror_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """
        Handles errors for the testerror command.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
            error (commands.CommandError): The error that occurred.
        """
        if isinstance(error, app_commands.CheckFailure):
            # Notify the user that only bot developers can run this command
            await self._send_embed(
                interaction,
                "Error",
                "Only the bot developer can run this command.",
                ERROR_EMBED_COLOR,
            )
        else:
            # Handle other errors using the global error handler
            await handle_error(interaction, error)

    @app_commands.command(
        name="restart", description="Restart the bot. Restricted to bot developers."
    )
    @app_commands.check(botownercheck)
    async def restart(self, interaction: discord.Interaction) -> None:
        """
        Restarts the bot.

        Args:
            interaction (discord.Interaction): The interaction that triggered the command.
        """

        if not CONFIG["advanced"]["linux_service_name"]:
            return await interaction.response.send_message(
                "The Linux service name is not set in the config file.", ephemeral=True
            )

        await interaction.response.send_message("Restarting the bot...", ephemeral=True)

        # Restart the bot using the Linux service
        os.system(
            "systemctl restart {}".format(CONFIG["advanced"]["linux_service_name"])
        )


async def setup(bot: commands.Bot) -> None:
    """
    Sets up the cog by adding it to the bot.

    Args:
        bot (commands.Bot): The instance of the bot to which this cog is added.
    """
    await bot.add_cog(RickBot_BotUtilsSlashCommands(bot))
