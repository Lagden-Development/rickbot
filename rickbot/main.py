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
from typing import Union, List, Optional, Any
from dataclasses import dataclass

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
from config import CONFIG, CUSTOM_CONFIG


@dataclass
class StatusConfig:
    """Configuration settings for bot status."""

    enabled: bool
    type: str
    text: str
    url: Optional[str] = None

    @classmethod
    def from_config(cls, config: dict) -> "StatusConfig":
        """Create a StatusConfig instance from a configuration dictionary."""
        return cls(
            enabled=config["BOT"]["status"] == "on",
            type=config["BOT"]["status_type"],
            text=config["BOT"]["status_text"],
            url=config["BOT"].get("status_url"),
        )


class WebhookFailedError(Exception):
    """Raised when a webhook fails to send a message after multiple attempts."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"Webhook failed after {attempts} attempts. Last error: {last_error}"
        )


def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """
    Determine the command prefix for the bot based on the message context.

    Args:
        bot: The bot instance.
        message: The message that triggered the prefix check.

    Returns:
        A list containing the bot mention and custom prefix.
    """
    return commands.when_mentioned_or(CONFIG["BOT"]["prefix"])(bot, message)


class RickContext(commands.Context):
    """
    Custom context class for RickBot with enhanced functionality.

    This class extends the default Context class to provide additional methods
    and properties specific to RickBot's requirements.
    """

    async def safe_send(self, content: str, **kwargs: Any) -> Optional[discord.Message]:
        """
        Safely send a message with error handling.

        Args:
            content: The message content to send.
            **kwargs: Additional keyword arguments for message sending.

        Returns:
            The sent message if successful, None otherwise.
        """
        try:
            return await self.send(content, **kwargs)
        except discord.HTTPException as e:
            RICKLOG_DISCORD.error(f"Failed to send message: {e}")
            return None


class RickBot(commands.Bot):
    """
    Custom bot class that encapsulates the main functionality of RickBot.

    This class extends discord.py's Bot class with enhanced initialization,
    event handling, and utility methods specific to RickBot's requirements.
    """

    def __init__(self) -> None:
        """Initialize the RickBot instance with custom configurations."""
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
        self.config = CONFIG
        self.custom_config = CUSTOM_CONFIG
        self.status_config: StatusConfig = StatusConfig.from_config(CONFIG)
        self._last_error: Optional[Exception] = None

    def setup_logging(self) -> None:
        """Configure logging with appropriate levels and handlers."""
        setup_discord_logging(logging.DEBUG)
        RICKLOG.setLevel(
            logging.DEBUG if CONFIG["MAIN"]["mode"] == "dev" else logging.INFO
        )

    def load_config(self) -> None:
        """Load and validate configuration settings."""
        if not all(
            key in CONFIG["BOT"]
            for key in ["prefix", "status", "status_type", "status_text"]
        ):
            raise ValueError("Missing required configuration keys in CONFIG['BOT']")

    async def setup_hook(self) -> None:
        """Perform asynchronous setup operations before bot login."""
        await self.load_cogs()

    async def load_cogs(self) -> None:
        """Load all cogs from the 'cogs' directory with error handling."""
        for cog_folder in glob.glob("cogs/*"):
            if cog_folder.startswith("_"):
                continue

            cogs_loaded: int = 0
            cog_errors: List[str] = []

            for filename in glob.glob(f"{cog_folder}/*.py"):
                if filename.startswith("_"):
                    continue

                try:
                    cog_name: str = f"{filename[:-3].replace('/', '.')}"
                    await self.load_extension(cog_name)
                    cogs_loaded += 1
                    RICKLOG_MAIN.debug(f"Loaded cog: {cog_name}")
                except Exception as e:
                    cog_errors.append(f"{filename}: {str(e)}")
                    RICKLOG_MAIN.error(f"Failed to load cog {filename}: {e}")

            RICKLOG_MAIN.info(f"Loaded cog folder: {cog_folder} ({cogs_loaded} cogs)")
            if cog_errors:
                RICKLOG_MAIN.warning(
                    f"Failed to load {len(cog_errors)} cogs in {cog_folder}"
                )

    async def get_context(
        self, message: discord.Message, *, cls: Optional[type] = None
    ) -> RickContext:
        """Create a custom context for command processing."""
        return await super().get_context(message, cls=RickContext)

    async def on_ready(self) -> None:
        """Handle bot ready event with enhanced status management."""
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_MAIN.info(
            f"RickBot started at {colored(current_time, 'light_cyan', attrs=['bold', 'underline'])}"
        )
        RICKLOG_DISCORD.info("RickBot's Connection to Discord initialized.")

        try:
            await self.set_status()
            rickbot_start_msg(self)
            print()

            RICKLOG_DISCORD.info("Syncing commands...")
            await self.tree.sync()
            RICKLOG_DISCORD.info("Commands synced.")
        except Exception as e:
            RICKLOG_MAIN.error(f"Error during startup: {e}")
            self._last_error = e

    async def set_status(self) -> None:
        """Set bot status based on configuration with improved error handling."""
        if not self.status_config.enabled:
            return

        try:
            activity: Optional[
                Union[discord.Game, discord.Activity, discord.Streaming]
            ] = None

            if self.status_config.type == "playing":
                activity = discord.Game(name=self.status_config.text)
            elif self.status_config.type in ("watching", "listening"):
                activity_type = getattr(discord.ActivityType, self.status_config.type)
                activity = discord.Activity(
                    type=activity_type, name=self.status_config.text
                )
            elif self.status_config.type == "streaming" and self.status_config.url:
                activity = discord.Streaming(
                    name=self.status_config.text, url=self.status_config.url
                )
            else:
                RICKLOG_MAIN.warning(f"Invalid status type: {self.status_config.type}")
                return

            if activity:
                await self.change_presence(activity=activity)

        except Exception as e:
            RICKLOG_MAIN.error(f"Failed to set status: {e}")

    async def on_message(self, message: discord.Message) -> None:
        """Process incoming messages with improved mention handling."""
        if message.author.bot or message.webhook_id:
            return

        if self.user and self.user.mentioned_in(message):
            try:
                await message.reply(
                    f"Hey there, {message.author.mention}! Use `{CONFIG['BOT']['prefix']}help` to see what I can do.",
                    mention_author=False,
                )
                return
            except discord.HTTPException as e:
                RICKLOG_DISCORD.error(f"Failed to send mention response: {e}")

        await self.process_commands(message)

    async def on_command_error(
        self, ctx: commands.Context, error: discord.DiscordException
    ) -> None:
        """Handle command errors with improved error categorization."""
        if hasattr(ctx.command, "on_error") or (
            ctx.cog and hasattr(ctx.cog, "cog_command_error")
        ):
            return

        if isinstance(error, commands.CommandNotFound):
            return

        self._last_error = error
        await handle_error(ctx, error)

    async def start_bot(self) -> None:
        """Start the bot with enhanced token validation and error handling."""
        token = os.getenv("TOKEN")
        if not token:
            raise ValueError(
                "No token provided. Please set the TOKEN environment variable or use the auto-setup script."
            )

        try:
            RICKLOG_MAIN.info("Starting RickBot...")
            await self.start(token)
        except discord.LoginFailure as e:
            RICKLOG_MAIN.error(f"Failed to login: Invalid token - {e}")
            raise
        except Exception as e:
            RICKLOG_MAIN.error(f"Failed to start bot: {e}")
            raise
        finally:
            RICKLOG_MAIN.info("Discord connection closed.")

    async def shutdown(self, signal: str) -> None:
        """Perform graceful shutdown with enhanced cleanup."""
        RICKLOG_MAIN.info(
            f"Received exit signal {signal} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}..."
        )

        try:
            RICKLOG_DISCORD.info("Closing Discord connection...")
            await self.close()
            RICKLOG_DISCORD.info("Discord connection closed.")
        except Exception as e:
            RICKLOG_MAIN.error(f"Error during shutdown: {e}")
            raise

    async def on_connect(self) -> None:
        """Log successful connection with enhanced session tracking."""
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(f"RickBot connected to Discord at {current_time}.")
        RICKLOG_DISCORD.info(f"Session ID: {self.ws.session_id}")

    async def on_disconnect(self) -> None:
        """Handle disconnection with improved state management."""
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.warning(f"RickBot disconnected from Discord at {current_time}.")

        if self.is_closed():
            RICKLOG_DISCORD.info("RickBot connection was intentionally closed.")
        else:
            RICKLOG_DISCORD.info(
                "RickBot disconnected unexpectedly, attempting to reconnect..."
            )

    async def on_resumed(self) -> None:
        """Handle session resume with enhanced logging."""
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        RICKLOG_DISCORD.info(f"RickBot resumed connection at {current_time}.")
        RICKLOG_DISCORD.info(f"Resumed Session ID: {self.ws.session_id}")
