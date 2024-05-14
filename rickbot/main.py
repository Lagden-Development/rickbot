"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the main application file for RickBot.
"""

# Import the required modules

# Python standard library
from datetime import datetime
import asyncio
import logging
import os

# Third-party libraries
from termcolor import colored

# discord.py library
from discord.ext import commands
import discord

# Helper files
from helpers.logs import RICKLOG, setup_discord_logging
from helpers.rickbot import rickbot_start_msg
from helpers.errors import handle_error

# Configuration file
from config import CONFIG

# Custom exceptions


class WebhookFailedError(Exception):
    """
    Raised when a webhook fails to send a message.
    """

    pass


# Classes


# Define the custom Context class
class RickContext(commands.Context):
    pass


# Define the custom Bot class
class RickBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=CONFIG["bot"]["prefix"], intents=discord.Intents.all()
        )

        self.setup_logging()
        self.load_config()

    def setup_logging(self):
        # Set the working directory to the directory of this file
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        # Set up the logging
        setup_discord_logging(logging.INFO)

    def load_config(self):
        if CONFIG["mode"] == "dev":
            RICKLOG.setLevel(logging.DEBUG)
        else:
            RICKLOG.setLevel(logging.INFO)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=RickContext)

    async def on_ready(self):
        self.user: discord.ClientUser = self.user

        RICKLOG.info(
            f"RickBot started at {colored(datetime.now(), 'light_cyan', attrs=['bold', 'underline'])}"
        )
        RICKLOG.info("RickBot's Connection to Discord initialized.")

        await self.set_status()
        rickbot_start_msg(self)

    async def set_status(self):
        """
        Update the bot's status based on the configuration file.
        """

        status_type = CONFIG["bot"]["status"]["type"]
        message = CONFIG["bot"]["status"]["message"]

        if status_type == "playing":
            await self.change_presence(activity=discord.Game(name=message))

        elif status_type == "watching":
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=message
                )
            )

        elif status_type == "listening":
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name=message
                )
            )

        elif status_type == "streaming":
            url = CONFIG["bot"]["status"]["url"]
            await self.change_presence(
                activity=discord.Streaming(name=message, url=url)
            )

    async def on_message(self, message):
        # Process commands and check for mentions
        if message.author == self.user or message.author.bot or message.guild is None:
            return

        if message.content.startswith(
            f"<@!{self.user.id}>"
        ) or message.content.startswith(f"<@{self.user.id}>"):
            await message.reply(
                f"Hey there, {message.author.mention}! Use `{CONFIG['bot']['prefix']}help` to see what I can do.",
                mention_author=False,
            )
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        # Error handling for commands without specific error handlers
        if hasattr(ctx.command, "on_error"):
            return
        await handle_error(ctx, error)

    async def start_bot(self):
        try:
            await self.start(CONFIG["bot"]["token"])
        finally:
            RICKLOG.info("RickBot has shut down gracefully.")

    async def shutdown(self, signal):
        """Gracefully shut down the bot."""
        RICKLOG.info(f"Received exit signal {signal.name}...")
        RICKLOG.info("Closing Discord connection...")
        await self.close()
        RICKLOG.info("Discord connection closed.")

    async def grab_channel_webhook(
        self, channel: discord.TextChannel
    ) -> discord.Webhook:
        """
        Grabs the first webhook found in a channel.
        For the webhooks it finds it has to ensure it was created by the bot.
        Otherwise (or if not found) it creates a new webhook.
        """

        # Grab all webhooks in the channel
        webhooks = await channel.webhooks()

        # Find all webhooks created by the bot
        bot_webhooks = [webhook for webhook in webhooks if webhook.user == self.user]

        # There should only be one webhook created by the bot
        # If there are more than one, delete the extras
        if len(bot_webhooks) > 1:
            for webhook in bot_webhooks[1:]:
                await webhook.delete()

        # If there are no webhooks created by the bot, create a new one
        if not bot_webhooks:
            webhook = await channel.create_webhook(
                name="BHB Logging",
                reason="Creating new webhook for logging.",
            )
        else:
            webhook = bot_webhooks[0]

        return webhook

    async def send_to_channel(
        self,
        channel: discord.TextChannel,
        **kwargs,
    ):
        """
        Sends a message to a channel using a webhook.
        """

        # Grab the webhook for the channel
        webhook = await self.grab_channel_webhook(channel)

        # Try to send the message
        # Allow 3 attempts

        for _ in range(3):
            try:
                await webhook.send(**kwargs)
                return
            except discord.HTTPException as e:
                RICKLOG.error(f"Failed to send message to channel {channel}: {e}")
                await asyncio.sleep(1)
