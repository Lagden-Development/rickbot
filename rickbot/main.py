"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This is the main application file for RickBot.
"""

# Python Standard Library Imports
# -------------------------------
from datetime import datetime  # Used for logging timestamps and bot status updates.
import asyncio  # Essential for managing asynchronous operations, which are critical for bot functionality.
import logging  # Provides logging capabilities to track events and debug issues.
import glob  # Used to find file paths matching a specified pattern, useful for loading cogs dynamically.

# Third-party Libraries
# ---------------------
from discord.ext import (
    commands,
)  # Imports the commands extension for creating and managing bot commands.
from termcolor import (
    colored,
)  # Used to add color to the console output, enhancing readability.
import discord  # Core library for interacting with the Discord API.

# Internal Modules
# ------------
from helpers.logs import (
    setup_discord_logging,  # Function to set up logging specifically for Discord-related events.
    RICKLOG,  # Main logger for general bot-related logging.
    RICKLOG_MAIN,  # Logger for logging the main bot events.
    RICKLOG_DISCORD,  # Logger for Discord-specific events.
    RICKLOG_WEBHOOK,  # Logger for webhook-related events.
)
from helpers.rickbot import (
    rickbot_start_msg,
)  # Function to print the bot start message.
from helpers.errors import (
    handle_error,
)  # Function to handle errors in a standardized way.
from db import bot_db  # Database connection for the bot.

# Configuration
# ------------------
from config import (
    CONFIG,
)  # Configuration settings.


# Configurations (Not usually changed, so not in the config file)
# ---------------------------------------------------------------
COMMAND_ERRORS_TO_IGNORE = (
    commands.CommandNotFound,
)  # A tuple of command errors that can be safely ignored.


# Custom Exceptions
# -----------------
class WebhookFailedError(Exception):
    """
    Raised when a webhook fails to send a message.
    """

    pass  # This exception is used to signal a failure in sending a webhook message.


# Functions
# ---------


def get_prefix(bot, message):
    """
    Function to determine the command prefix for the bot.

    Args:
        bot: The instance of the bot.
        message: The message object which triggered the command.

    Returns:
        Callable: A function that returns either the mentioned prefix or the prefix defined in the configuration.
    """
    return commands.when_mentioned_or(CONFIG["BOT"]["prefix"])(bot, message)


# Classes
# -------
class RickContext(commands.Context):
    """
    Custom context class for the bot, used to override or extend the default context behavior.
    """


class RickBot(commands.Bot):
    """
    Custom bot class that encapsulates the main functionality and behavior of RickBot.
    """

    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,  # Sets the prefix used to invoke commands.
            case_insensitive=True,  # Commands are case-insensitive, making them easier to use.
            strip_after_prefix=True,  # Strips whitespace after the prefix, ensuring clean command parsing.
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False
            ),  # Prevents mass mentions.
            intents=discord.Intents.all(),  # Sets the bot's intents, enabling access to all necessary events.
        )

        self.setup_logging()  # Initialize logging setup.
        self.load_config()  # Load configuration settings.

    def setup_logging(self):
        """
        Sets up the logging configuration for the bot.
        """
        setup_discord_logging(
            logging.DEBUG
        )  # Calls a helper function to configure Discord-specific logging.

    def load_config(self):
        """
        Loads and applies the bot's configuration settings.
        Adjusts logging levels based on the current mode (development or production).
        """
        if CONFIG["MAIN"]["mode"] == "dev":
            RICKLOG.setLevel(
                logging.DEBUG
            )  # Enables debug logging in development mode.
        else:
            RICKLOG.setLevel(
                logging.INFO
            )  # Uses standard logging levels in production.

    async def setup_hook(self):
        """
        Runs after the bot has connected but before it has logged in.
        Used here to load all the cogs.
        """
        await self.load_cogs()  # Calls a method to dynamically load all bot cogs.

    async def load_cogs(self):
        """
        Loads all cogs (extensions) from the 'cogs' directory.
        """
        for cog_folder in glob.glob("cogs/*"):
            cogs_loaded_from_this_folder = 0
            if not cog_folder.startswith("_"):
                for filename in glob.glob(f"{cog_folder}/*.py"):
                    if not filename.startswith("_"):
                        cog_name = f"{filename[:-3].replace('/', '.')}"  # Convert file path to module path.
                        await self.load_extension(
                            cog_name
                        )  # Load the cog as an extension.
                        cogs_loaded_from_this_folder += 1
                        RICKLOG_MAIN.debug(
                            f"Loaded cog: {cog_name}"
                        )  # Log the cog loading.

            RICKLOG_MAIN.info(
                f"Loaded cog folder: {cog_folder} ({cogs_loaded_from_this_folder} cogs)"
            )

    async def get_context(self, message, *, cls=None):
        """
        Overrides the default context method to use RickContext.

        Args:
            message: The message that triggered the context creation.
            cls: The class to use for context creation (defaults to RickContext).

        Returns:
            RickContext: The context object created for the message.
        """
        return await super().get_context(message, cls=RickContext)

    async def on_ready(self):
        """
        Called when the bot is ready and fully connected to Discord.
        Logs the ready state and sets the bot's status.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_MAIN.info(
            f"RickBot started at {colored(current_time, 'light_cyan', attrs=['bold', 'underline'])}"
        )
        RICKLOG_DISCORD.info("RickBot's Connection to Discord initialized.")

        await self.set_status()  # Set the bot's status according to the configuration.
        rickbot_start_msg(self)  # Display the start message.
        print()  # Print an empty line for better console readability.

        RICKLOG_DISCORD.info("Syncing commands...")
        await self.tree.sync()  # Sync commands with Discord.
        RICKLOG_DISCORD.info("Commands synced.")

    async def set_status(self):
        """
        Update the bot's status based on the configuration file.
        """

        status_type = CONFIG["BOT"]["status_type"]
        message = CONFIG["BOT"]["status_text"]

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
            url = CONFIG["BOT"]["status_url"]
            await self.change_presence(
                activity=discord.Streaming(name=message, url=url)
            )

    async def on_message(self, message):
        """
        Handles incoming messages and processes commands.

        Args:
            message: The message object representing the received message.
        """
        # Ignore messages from the bot itself, other bots, DMs, or webhooks.
        if message.author == self.user or message.author.bot or message.webhook_id:
            return

        # Check if the message mentions the bot and respond with a help message.
        if message.content.startswith(
            f"<@!{self.user.id}>"
        ) or message.content.startswith(f"<@{self.user.id}>"):
            await message.reply(
                f"Hey there, {message.author.mention}! Use `{CONFIG['BOT']['prefix']}help` to see what I can do.",
                mention_author=False,
            )
            return

        await self.process_commands(message)  # Process commands in the message.

    async def on_command_error(self, ctx, error):
        """
        Global error handler for commands.

        Args:
            ctx: The context in which the error occurred.
            error: The error that occurred.
        """
        # If the command has its own error handler or the error should be ignored, do nothing.
        if hasattr(ctx.command, "on_error") or isinstance(
            error, COMMAND_ERRORS_TO_IGNORE
        ):
            return

        await handle_error(ctx, error)  # Handle the error using a custom handler.

    async def start_bot(self):
        """
        Starts the bot and handles graceful shutdown.

        This method encapsulates the bot's startup process and ensures that
        the bot shuts down gracefully when requested.
        """
        try:
            RICKLOG_MAIN.info("Starting RickBot...")
            await self.start(
                CONFIG["BOT"]["token"]
            )  # Start the bot using the token from the config.
        finally:
            RICKLOG_MAIN.info(
                "RickBot has shut down gracefully."
            )  # Log that the bot has shut down.

    async def shutdown(self, signal):
        """
        Gracefully shuts down the bot upon receiving a termination signal.

        Args:
            signal: The signal that triggered the shutdown.
        """
        RICKLOG_MAIN.info(
            f"Received exit signal {signal.name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}..."
        )
        RICKLOG_DISCORD.info("Closing Discord connection...")
        await self.close()  # Close the connection to Discord.
        RICKLOG_DISCORD.info("Discord connection closed.")

    async def on_connect(self):
        """
        Called when the bot successfully connects to Discord.
        Logs the connection event.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(f"RickBot connected to Discord at {current_time}.")
        RICKLOG_DISCORD.info(f"Session ID: {self.ws.session_id}")  # Log the session ID.

    async def on_disconnect(self):
        """
        Called when the bot disconnects from Discord.
        Logs the disconnection event and attempts to reconnect.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.warning(f"RickBot disconnected from Discord at {current_time}.")
        RICKLOG_DISCORD.info("Attempting to reconnect...")

    async def on_resumed(self):
        """
        Called when the bot successfully resumes a connection to Discord after a disconnect.
        Logs the resume event.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(
            f"RickBot resumed connection to Discord at {current_time}."
        )
        RICKLOG_DISCORD.info(
            f"Resumed Session ID: {self.ws.session_id}"
        )  # Log the resumed session ID.

    async def grab_channel_webhook(
        self, channel: discord.TextChannel
    ) -> discord.Webhook:
        """
        Grabs or creates a webhook for the specified channel.

        Args:
            channel (discord.TextChannel): The channel for which the webhook is being retrieved or created.

        Returns:
            discord.Webhook: The webhook object for the specified channel.
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

        Args:
            channel (discord.TextChannel): The channel where the message will be sent.
            **kwargs: Additional keyword arguments to be passed to the webhook's send method.
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
                await asyncio.sleep(1)  # Wait for a second before retrying.
