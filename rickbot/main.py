"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the main application file for RickBot.
"""

# Python standard library
from datetime import datetime
import asyncio
import logging
import glob

# Third-party libraries
from termcolor import colored

# discord.py library
from discord.ext import commands
import discord

# Helper files
from helpers.logs import (
    setup_discord_logging,
    RICKLOG,
    RICKLOG_MAIN,
    RICKLOG_DISCORD,
    RICKLOG_WEBHOOK,
)
from helpers.rickbot import rickbot_start_msg
from helpers.errors import handle_error

# Configuration file
from config import CONFIG

# Configurations (Not usally changed, so not in the config file)

COMMAND_ERRORS_TO_IGNORE = (commands.CommandNotFound,)

# Custom exceptions


class WebhookFailedError(Exception):
    """
    Raised when a webhook fails to send a message.
    """

    pass


# Functions


def get_prefix(bot, message):
    return commands.when_mentioned_or(CONFIG["bot"]["prefix"])(bot, message)


# Classes


# Define the custom Context class
class RickContext(commands.Context):
    pass


# Define the custom Bot class
class RickBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            strip_after_prefix=True,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
            intents=discord.Intents.all(),
        )

        self.setup_logging()
        self.load_config()

    def setup_logging(self):
        setup_discord_logging(logging.INFO)

    def load_config(self):
        if CONFIG["mode"] == "dev":
            RICKLOG.setLevel(logging.DEBUG)
        else:
            RICKLOG.setLevel(logging.INFO)

    async def setup_hook(self):
        await self.load_cogs()

    async def load_cogs(self):
        for cog_folder in glob.glob("cogs/*"):
            cogs_loaded_from_this_folder = 0
            if not cog_folder.startswith("_"):
                for filename in glob.glob(f"{cog_folder}/*.py"):
                    if not filename.startswith("_"):
                        cog_name = f"{filename[:-3].replace('/', '.')}"
                        await self.load_extension(cog_name)
                        cogs_loaded_from_this_folder += 1

                        RICKLOG_MAIN.debug(f"Loaded cog: {cog_name}")

            RICKLOG_MAIN.info(
                f"Loaded cog folder: {cog_folder} ({cogs_loaded_from_this_folder} cogs)"
            )

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=RickContext)

    async def on_ready(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_MAIN.info(
            f"RickBot started at {colored(current_time, 'light_cyan', attrs=['bold', 'underline'])}"
        )
        RICKLOG_DISCORD.info("RickBot's Connection to Discord initialized.")

        await self.set_status()
        rickbot_start_msg(self)
        print()

        RICKLOG_DISCORD.info("Syncing commands...")
        await self.tree.sync()
        RICKLOG_DISCORD.info("Commands synced.")

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
        if (
            message.author == self.user
            or message.author.bot
            or message.guild is None
            or message.webhook_id
        ):
            return

        if message.content.startswith(
            f"<@!{self.user.id}>"  # type: ignore
        ) or message.content.startswith(
            f"<@{self.user.id}>"  # type: ignore
        ):
            await message.reply(
                f"Hey there, {message.author.mention}! Use `{CONFIG['bot']['prefix']}help` to see what I can do.",
                mention_author=False,
            )
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        # Error handling for commands without specific error handlers
        if hasattr(ctx.command, "on_error") or isinstance(
            error, COMMAND_ERRORS_TO_IGNORE
        ):
            return

        await handle_error(ctx, error)

    async def start_bot(self):
        try:
            RICKLOG_MAIN.info("Starting RickBot...")
            await self.start(CONFIG["bot"]["token"])
        finally:
            RICKLOG_MAIN.info("RickBot has shut down gracefully.")

    async def shutdown(self, signal):
        """Gracefully shut down the bot."""
        RICKLOG_MAIN.info(
            f"Received exit signal {signal.name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}..."
        )
        RICKLOG_DISCORD.info("Closing Discord connection...")
        await self.close()
        RICKLOG_DISCORD.info("Discord connection closed.")

    async def on_connect(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(f"RickBot connected to Discord at {current_time}.")
        RICKLOG_DISCORD.info(f"Session ID: {self.ws.session_id}")

    async def on_disconnect(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.warning(f"RickBot disconnected from Discord at {current_time}.")
        RICKLOG_DISCORD.info("Attempting to reconnect...")

    async def on_resumed(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(
            f"RickBot resumed connection to Discord at {current_time}."
        )
        RICKLOG_DISCORD.info(f"Resumed Session ID: {self.ws.session_id}")

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
                name=self.user.display_name,
                reason=f"Creating new webhook for {self.user.display_name}",
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

        for attempt in range(3):
            try:
                await webhook.send(**kwargs)
                return
            except discord.HTTPException as e:
                RICKLOG_WEBHOOK.error(
                    f"Failed to send webhook message to channel {channel} on attempt ({str(attempt)}): {e}"
                )
                await asyncio.sleep(1)
