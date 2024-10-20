"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This module provides enhanced error handling functionality for discord.py related errors.
It includes a comprehensive error handling system that logs errors, notifies users,
and provides detailed information for debugging purposes, with improved user interaction.
"""

from typing import Union, Callable, Dict, Type, Optional
from datetime import datetime
import random
import string
import traceback
from pathlib import Path

import discord
from discord.ext import commands

from helpers.colors import ERROR_EMBED_COLOR
from helpers.logs import RICKLOG_MAIN

from config import CONFIG

# Directory for storing error logs
ERROR_DIR = Path(CONFIG["MAIN"]["error_log_folder"])


class CustomError(Exception):
    """
    Base class for custom errors in the RickBot system.

    Attributes:
        message (str): The error message.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InputValidationError(CustomError):
    """
    Raised when input validation fails.

    This error is used when user input does not meet the required criteria.
    """

    pass


class DatabaseError(CustomError):
    """
    Raised when a database operation fails.

    This error is used for any issues related to database interactions.
    """

    pass


class APIError(CustomError):
    """
    Raised when an API request fails.

    This error is used for issues related to external API calls.
    """

    pass


class ErrorDetailsView(discord.ui.View):
    """
    A view that provides a button to show detailed error information.

    Attributes:
        error_details (str): The detailed error message to be displayed.
    """

    def __init__(self, error_details: str):
        super().__init__()
        self.error_details = error_details

    @discord.ui.button(label="Show Details", style=discord.ButtonStyle.primary)
    async def show_details(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the "Show Details" button.

        Args:
            interaction (discord.Interaction): The interaction that triggered the button.
            button (discord.ui.Button): The button that was pressed.
        """
        await interaction.response.send_message(
            f"Error Details:\n```{self.error_details}```", ephemeral=True
        )


async def handle_error(
    ctx: Union[commands.Context, discord.Interaction], error: discord.DiscordException
) -> None:
    """
    Handles errors that occur within the bot by sending an appropriate response to the user
    and logging the error if necessary.

    This function categorizes errors, provides user-friendly messages, logs unexpected errors,
    and notifies the developer with detailed error information.

    Args:
        ctx (Union[commands.Context, discord.Interaction]): The context or interaction in which the error occurred.
        error (discord.DiscordException): The error that occurred.

    Returns:
        None

    Raises:
        No exceptions are raised by this function.
    """

    async def send_embed(
        embed: discord.Embed, view: Optional[discord.ui.View] = None
    ) -> None:
        """
        Helper function to send an embed depending on the context type.

        Args:
            embed (discord.Embed): The embed to send.
            view (Optional[discord.ui.View]): The view to attach to the message.

        Returns:
            None
        """
        if isinstance(ctx, commands.Context):
            await ctx.reply(
                embed=embed, view=view or discord.ui.View(), mention_author=False
            )
        elif isinstance(ctx, discord.Interaction):
            if not ctx.response.is_done():
                await ctx.response.send_message(
                    embed=embed, view=view or discord.ui.View(), ephemeral=True
                )
            else:
                await ctx.followup.send(
                    embed=embed, view=view or discord.ui.View(), ephemeral=True
                )

    # Dictionary mapping error types to their corresponding user-friendly messages
    error_handlers: Dict[Type[Exception], Union[str, Callable]] = {
        commands.CommandNotFound: "The command you entered was not found. Please check the spelling and try again.",
        commands.MissingRequiredArgument: lambda e: f"Missing required argument: {e.param.name}. Please provide all necessary information.",
        commands.BadArgument: "Invalid argument provided. Please check the command usage and try again.",
        commands.MissingPermissions: lambda e: f"You lack the following required permissions: {', '.join(e.missing_permissions)}.",
        commands.BotMissingPermissions: lambda e: f"The bot lacks the following required permissions: {', '.join(e.missing_permissions)}.",
        commands.CommandOnCooldown: lambda e: f"This command is on cooldown. Please try again in {e.retry_after:.2f} seconds.",
        commands.CheckFailure: "You do not meet the requirements to use this command. Please check your roles and permissions.",
        OverflowError: "The number you entered is too large for the system to handle. Please use a smaller value.",
        InputValidationError: lambda e: f"Input validation failed: {e.message}",
        DatabaseError: lambda e: f"A database error occurred: {e.message}",
        APIError: lambda e: f"An API error occurred: {e.message}",
    }

    # Generate a unique error ID
    error_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Check for known error types and handle them
    for error_type, message in error_handlers.items():
        if isinstance(error, error_type):
            error_message = message if isinstance(message, str) else message(error)
            break
    else:
        # Handle unexpected errors
        error_message = (
            "An unexpected error has occurred. Our team has been notified and is working on a solution.\n\n"
            "If this issue persists, please contact our support team and provide the Error ID below."
        )

    embed = discord.Embed(
        title="Error Occurred" if error_message else "Unexpected Error",
        description=error_message,
        color=ERROR_EMBED_COLOR,
        timestamp=datetime.now() if error_message else None,
    )
    embed.set_footer(text="For more information, click the button below.")
    embed.add_field(name="Error ID", value=f"```{error_id}```", inline=False)

    error_details = (
        f"An unexpected error occurred (ID: {error_id}).\nError: {str(error)}"
        if not error_message
        else error_message
    )
    view = ErrorDetailsView(error_details)

    await send_embed(embed, view)

    # Log the error details
    ERROR_DIR.mkdir(exist_ok=True)
    error_file = (
        ERROR_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{error_id}.txt"
    )

    original_error = getattr(error, "original", error)
    traceback_error = traceback.format_exception(
        type(original_error), original_error, original_error.__traceback__
    )

    with error_file.open("w") as f:
        f.write(
            "Error Report for RickBot\n"
            "========================\n\n"
            "An error occurred during the execution of RickBot.\n"
            "This report contains detailed information about the error for debugging purposes.\n\n"
        )
        f.write(f"Error: {error}\n")
        f.write(f"Error ID: {error_id}\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"User-friendly message: {error_message}\n\n")
        if isinstance(ctx, commands.Context):
            f.write(f"Command: {ctx.command}\n")
            f.write(f"Author: {ctx.author} (ID: {ctx.author.id})\n")
            f.write(f"Message Content: {ctx.message.content}\n")
            f.write(
                f"Guild: {ctx.guild} (ID: {ctx.guild.id if ctx.guild else 'N/A'})\n"
            )
            f.write(f"Channel: {ctx.channel} (ID: {ctx.channel.id})\n")
        elif isinstance(ctx, discord.Interaction):
            f.write(f"Command: {ctx.command.name if ctx.command else 'N/A'}\n")
            f.write(f"User: {ctx.user} (ID: {ctx.user.id})\n")
            f.write(
                f"Guild: {ctx.guild} (ID: {ctx.guild.id if ctx.guild else 'N/A'})\n"
            )
            f.write(
                f"Channel: {ctx.channel} (ID: {ctx.channel.id if ctx.channel else 'N/A'})\n"
            )
        f.write("\n\nTraceback\n" "=========\n\n")
        f.write("".join(traceback_error))

    RICKLOG_MAIN.error(f"Error occurred (ID: {error_id}): {error}")
    RICKLOG_MAIN.error(f"Detailed error log created at {error_file}")
