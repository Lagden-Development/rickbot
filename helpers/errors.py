"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This is a helper for handling all discord.py related errors.
"""

# Import the required modules

# Python Standard Library
# ------------------------
from datetime import (
    datetime,
)  # Used for timestamping error logs and embeds with the current date and time.
import os  # Interacts with the operating system, here to check and create directories.
import random  # Used to generate random values, specifically for creating unique error IDs.
import string  # Provides a set of characters used in the creation of random error IDs.
import traceback  # Captures and formats stack traces, useful for detailed error logs.

# Third Party Libraries
# ---------------------
import discord  # The primary library for interacting with the Discord API.
from discord.ext import (
    commands,
)  # Provides the Command extension for building Discord bots.

# Internal Modules
# ----------------
from helpers.colors import ERROR_EMBED_COLOR  # Custom color code for error embeds.
from helpers.logs import (
    RICKLOG_MAIN,
)  # The main logger for RickBot, used to log error details.


async def handle_error(ctx: commands.Context, error: discord.DiscordException) -> None:
    """
    Handles errors that occur within the bot by sending an appropriate response to the user
    and logging the error if necessary.

    Args:
        ctx (commands.Context): The context in which the error occurred.
        error (discord.DiscordException): The error that occurred.

    Returns:
        None
    """
    # Check for specific command-related errors and handle them accordingly
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

    elif isinstance(error, OverflowError):
        embed = discord.Embed(
            title="Error",
            description="The number you entered is too large.",
            color=ERROR_EMBED_COLOR,
        )
        await ctx.reply(embed=embed, mention_author=False)

    else:
        # Handle unexpected errors by logging and informing the user
        # Generate a random error ID to track this specific error instance
        error_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        embed = discord.Embed(
            title="An Unexpected Error has occurred",
            description=(
                "You should feel special, this doesn't often happen.\n\n"
                "The developer has been notified, and a fix should be out soon.\n"
                "If no fix has been released after a while, please contact the "
                "developer and provide the below Error ID."
            ),
            timestamp=datetime.now(),
            color=ERROR_EMBED_COLOR,
        )

        embed.add_field(name="Error", value=f"```{error}```", inline=False)
        embed.add_field(name="Error ID", value=f"```{error_id}```", inline=False)
        embed.set_footer(text="RickBot Error Logging")

        # Ensure the errors directory exists, create it if it doesn't
        if not os.path.exists("errors"):
            RICKLOG_MAIN.warning(
                "The errors directory does not exist; creating it now."
            )
            try:
                os.makedirs("errors")
            except Exception as e:
                RICKLOG_MAIN.error(
                    f"An error occurred while creating the errors directory: {e}\nNo error log will be created."
                )
                return

        # Log the error details to a file in the errors directory
        error_file = (
            f"errors/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{error_id}.txt"
        )

        # Capture the original error's traceback for detailed logging
        original_error = error.original
        traceback_error = traceback.format_exception(
            type(original_error), original_error, original_error.__traceback__
        )

        with open(error_file, "w+") as f:
            f.write(
                "Hello! An error occurred during the running of RickBot.\n"
                "This is most likely a serious error, so please investigate it.\n"
                "If you find this error has occurred due to an issue with the original code, "
                "please contact the developer.\nOtherwise, you're on your own. Good luck!\n\n"
            )
            f.write(f"Error: {error}\n")
            f.write(f"Error ID: {error_id}\n")
            f.write(f"Command: {ctx.command}\n")
            f.write(f"Author: {ctx.author}\n")
            f.write(f"Message: {ctx.message.content}\n")
            f.write(f"Guild: {ctx.guild}\n")
            f.write(f"Channel: {ctx.channel}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(
                "\n\n----------------------------------------------------\nTraceback\n"
                "----------------------------------------------------\n\n\n"
            )
            f.write("".join(traceback_error))

        # Inform the user of the error and log it
        await ctx.reply(embed=embed, mention_author=False)
        RICKLOG_MAIN.error(f"An error occurred while running the command: {error}")
        RICKLOG_MAIN.error(f"Error log created at {error_file}")
