"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is a helper for handling all discord.py related errors.
"""

# Import the required modules

# Python standard library
from datetime import datetime
from requests.auth import HTTPBasicAuth
import os
import random
import requests
import string
import traceback

# Third-party libraries
import discord
from discord.ext import commands

# Helper functions
from helpers.colors import ERROR_EMBED_COLOR
from helpers.logs import RICKLOG_MAIN

# Config
from config import CUSTOM_CONFIG


def upload_to_paste(error_file_path):
    base_url = CUSTOM_CONFIG["apis"]["zl_paste"]["url"]
    paste_route = CUSTOM_CONFIG["apis"]["zl_paste"]["routes"]["paste"]
    auth = CUSTOM_CONFIG["apis"]["zl_paste"]["auth"]
    documents_url = f"{base_url}{paste_route}"

    with open(error_file_path, "r") as file:
        content = file.read()

    response = requests.post(
        documents_url,
        data=content,
        auth=HTTPBasicAuth(auth["username"], auth["password"]),
    )

    if response.status_code == 200:
        return f"{base_url}/{response.json()['key']}"
    else:
        RICKLOG_MAIN.critical(f"Failed to upload to Paste: {response.status_code}")
        RICKLOG_MAIN.exception(response.text)
        return None


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

    elif isinstance(error, OverflowError):
        embed = discord.Embed(
            title="Error",
            description="The number you entered is too large.",
            color=ERROR_EMBED_COLOR,
        )

        await ctx.reply(embed=embed, mention_author=False)

    else:
        # Generate a random error ID
        error_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        embed = discord.Embed(
            title="An Unexpected Error has occurred",
            description="You should feel special, this doesn't often happen.\n\nThe developer has been notified, "
            "and a fix should be out soon.\nIf no fix has been released after a while please contact the "
            "developer and provide the below Error ID.",
            timestamp=datetime.now(),
            color=ERROR_EMBED_COLOR,
        )

        embed.add_field(name="Error", value=f"```{error}```", inline=False)
        embed.add_field(name="Error ID", value=f"```{error_id}```", inline=False)

        embed.set_footer(text="RickBot Error Logging")

        # This is a serious error, log it in the errors directory

        # Ensure the errors directory exists
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

        # Log the error
        error_file = (
            f"errors/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{error_id}.txt"
        )

        with open(error_file, "w+") as f:
            f.write(
                "Hello! An error occurred during the running of RickBot.\nThis is most likely a serious error, "
                "so please investigate it.\nIf you find this errors has occurred due to an issue with the original "
                "code, please contact the developer.\nOtherwise, you're on your own. Good luck!\n\n"
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
            f.write(traceback.format_exc())

        paste_link = upload_to_paste(error_file)

        if paste_link:
            embed.add_field(
                name="Error Log",
                value=f"[View as Paste]({paste_link})",
                inline=False,
            )

        await ctx.reply(embed=embed, mention_author=False)

        RICKLOG_MAIN.error(f"An error occurred while running the command: {error}")
        RICKLOG_MAIN.error(f"Error log created at {error_file}")
        RICKLOG_MAIN.error(f"Paste link: {paste_link}")
