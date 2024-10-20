"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This is the main application file for RickBot, a Discord bot built using discord.py.
It contains the core functionality for bot initialization, command handling, and event management.
"""

from datetime import datetime
import logging
import glob
import os
from typing import Union, List, Optional

from pymongo.database import Database
from discord.ext import commands
from termcolor import colored
import discord

from helpers.logs import (
    setup_discord_logging,
    RICKLOG,
    RICKLOG_MAIN,
    RICKLOG_DISCORD,
)
from helpers.rickbot import rickbot_start_msg
from helpers.errors import handle_error
from db import bot_db
from config import CONFIG

COMMAND_ERRORS_TO_IGNORE = (commands.CommandNotFound,)


class WebhookFailedError(Exception):
    """
    Custom exception raised when a webhook fails to send a message after multiple attempts.

    This exception is used to signal that all attempts to send a message via webhook have failed,
    allowing for appropriate error handling and logging.
    """


def get_prefix(bot: commands.Bot, message: discord.Message) -> Union[List[str], str]:
    """
    Determine the command prefix for the bot based on the message context.

    This function returns either a mention of the bot or the configured prefix.
    It allows for flexible prefix handling, supporting both mentions and custom prefixes.

    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message that triggered the prefix check.

    Returns:
        Union[List[str], str]: A list containing the bot mention and custom prefix, or just the custom prefix.
    """
    return commands.when_mentioned_or(CONFIG["BOT"]["prefix"])(bot, message)


class RickContext(commands.Context):
    """
    Custom context class for RickBot.

    This class extends the default Context class from discord.py, allowing for
    additional custom functionality or attributes specific to RickBot's needs.
    It can be used to add custom methods or properties that are accessible in all command contexts.
    """


class RickBot(commands.Bot):
    """
    Custom bot class that encapsulates the main functionality and behavior of RickBot.

    This class extends discord.py's Bot class, implementing custom initialization,
    event handling, and utility methods specific to RickBot's requirements.
    """

    def __init__(self: "RickBot") -> None:
        """
        Initialize the RickBot instance.

        Sets up the bot with custom configurations including command prefix,
        intents, and allowed mentions. It also initializes logging and loads
        the bot's configuration.
        """
        intents: discord.Intents = discord.Intents.all()
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            strip_after_prefix=True,
            allowed_mentions=discord.AllowedMentions.all(),
            intents=intents,
        )
        self.setup_logging()
        self.load_config()
        self.db: Database = bot_db

    def setup_logging(self: "RickBot") -> None:
        """
        Set up the logging configuration for the bot.

        Configures logging levels and handlers for different parts of the bot,
        ensuring appropriate logging for debugging and monitoring.
        """
        setup_discord_logging(logging.DEBUG)

    def load_config(self: "RickBot") -> None:
        """
        Load and apply the bot's configuration settings.

        Reads the configuration file and sets appropriate logging levels
        based on whether the bot is running in development or production mode.
        """
        RICKLOG.setLevel(
            logging.DEBUG if CONFIG["MAIN"]["mode"] == "dev" else logging.INFO
        )

    async def setup_hook(self: "RickBot") -> None:
        """
        Run after the bot has connected but before it has logged in.

        This method is used to perform any asynchronous setup operations,
        such as loading cogs, before the bot becomes fully operational.
        """
        await self.load_cogs()

    async def load_cogs(self: "RickBot") -> None:
        """
        Load all cogs (extensions) from the 'cogs' directory.

        Iterates through the cogs directory, loading each Python file as a cog.
        This method allows for modular bot functionality through cogs.
        """
        for cog_folder in glob.glob("cogs/*"):
            if cog_folder.startswith("_"):
                continue
            cogs_loaded: int = 0
            for filename in glob.glob(f"{cog_folder}/*.py"):
                if filename.startswith("_"):
                    continue
                cog_name: str = f"{filename[:-3].replace('/', '.')}"
                await self.load_extension(cog_name)
                cogs_loaded += 1
                RICKLOG_MAIN.debug(f"Loaded cog: {cog_name}")
            RICKLOG_MAIN.info(f"Loaded cog folder: {cog_folder} ({cogs_loaded} cogs)")

    async def get_context(
        self: "RickBot", message: discord.Message, *, cls: Optional[type] = None
    ) -> RickContext:
        """
        Override the default context method to use RickContext.

        This method ensures that all command invocations use the custom RickContext,
        allowing for bot-specific context handling and features.

        Args:
            self (RickBot): The bot instance.
            message (discord.Message): The message that triggered the context creation.
            cls (Optional[type]): The class to use for context creation. Defaults to None.

        Returns:
            RickContext: The custom context object for the given message.
        """
        return await super().get_context(message, cls=RickContext)

    async def on_ready(self: "RickBot") -> None:
        """
        Event handler called when the bot is ready and fully connected to Discord.

        This method logs the bot's successful startup, sets the bot's status,
        displays the start message, and syncs slash commands with Discord.
        """
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

    async def set_status(self: "RickBot") -> None:
        """
        Update the bot's status based on the configuration file.

        Sets the bot's activity status on Discord according to the settings
        specified in the configuration file, supporting various activity types.
        """
        status_type: str = CONFIG["BOT"]["status_type"]
        message: str = CONFIG["BOT"]["status_text"]

        activity: Optional[Union[discord.Game, discord.Activity, discord.Streaming]] = (
            None
        )
        if status_type == "playing":
            activity = discord.Game(name=message)
        elif status_type in ("watching", "listening"):
            activity_type: discord.ActivityType = getattr(
                discord.ActivityType, status_type
            )
            activity = discord.Activity(type=activity_type, name=message)
        elif status_type == "streaming":
            url: str = CONFIG["BOT"]["status_url"]
            activity = discord.Streaming(name=message, url=url)

        if activity:
            await self.change_presence(activity=activity)

    async def on_message(self: "RickBot", message: discord.Message) -> None:
        """
        Event handler for processing incoming messages.

        This method handles bot mentions and processes commands. It ignores messages
        from bots and webhooks to prevent potential loops or unwanted interactions.

        Args:
            message (discord.Message): The message received by the bot.
        """
        if message.author.bot or message.webhook_id:
            return

        if self.user and (
            message.content.startswith(f"<@!{self.user.id}>")
            or message.content.startswith(f"<@{self.user.id}>")
        ):
            await message.reply(
                f"Hey there, {message.author.mention}! Use `{CONFIG['BOT']['prefix']}help` to see what I can do.",
                mention_author=False,
            )
            return

        await self.process_commands(message)

    async def on_command_error(
        self: "RickBot", ctx: commands.Context, error: discord.DiscordException
    ) -> None:
        """
        Global error handler for command-related errors.

        This method catches and processes errors that occur during command execution.
        It ignores certain types of errors and delegates others to a custom error handler.

        Args:
            ctx (commands.Context): The context in which the error occurred.
            error (discord.DiscordException): The error that was raised.
        """
        if hasattr(ctx.command, "on_error") or isinstance(
            error, COMMAND_ERRORS_TO_IGNORE
        ):
            return
        await handle_error(ctx, error)

    async def start_bot(self: "RickBot") -> None:
        """
        Start the bot and handle graceful shutdown.

        This method initiates the bot's connection to Discord and ensures
        proper shutdown procedures are followed when the bot is stopped.
        """
        try:
            RICKLOG_MAIN.info("Starting RickBot...")
            token = os.getenv("TOKEN")
            if not token:
                raise ValueError(
                    "No token provided. Please set the TOKEN environment variable, or use the auto-setup script to generate one, to run the setup, delete the .env file."
                )
            await self.start(token)
        finally:
            RICKLOG_MAIN.info("Discord connection closed.")

    async def shutdown(self: "RickBot", signal: str) -> None:
        """
        Gracefully shut down the bot upon receiving a termination signal.

        This method ensures that the bot performs necessary cleanup operations
        and closes its connection to Discord when a shutdown signal is received.

        Args:
            signal: The termination signal received.
        """
        RICKLOG_MAIN.info(
            f"Received exit signal {signal} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}..."
        )
        RICKLOG_DISCORD.info("Closing Discord connection...")
        await self.close()
        RICKLOG_DISCORD.info("Discord connection closed.")

    async def on_connect(self: "RickBot") -> None:
        """
        Event handler called when the bot successfully connects to Discord.

        This method logs the connection event and the session ID for debugging purposes.
        """
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(f"RickBot connected to Discord at {current_time}.")
        RICKLOG_DISCORD.info(f"Session ID: {self.ws.session_id}")

    async def on_disconnect(self: "RickBot") -> None:
        """
        Event handler called when the bot disconnects from Discord.

        This method logs the disconnection event and indicates that a reconnection attempt will be made.
        """
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.warning(f"RickBot disconnected from Discord at {current_time}.")
        # Check if the bot was disconnected on purpose
        if self.is_closed():
            RICKLOG_DISCORD.info(
                "RickBot connection to discord was intentionally closed."
            )
        else:
            RICKLOG_DISCORD.info(
                "RickBot was disconnected from discord unexpectedly, attempting to reconnect..."
            )

    async def on_resumed(self: "RickBot") -> None:
        """
        Event handler called when the bot successfully resumes a connection to Discord after a disconnect.

        This method logs the successful resumption of the connection and the new session ID.
        """
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(
            f"RickBot resumed connection to Discord at {current_time}."
        )
        RICKLOG_DISCORD.info(f"Resumed Session ID: {self.ws.session_id}")
