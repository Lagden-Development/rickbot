"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Core Bot Class

Production-grade Discord bot with integrated database observability.
"""

from typing import Optional
import discord
from discord.ext import commands, tasks
from motor.motor_asyncio import AsyncIOMotorClient
import time
import logging
from pathlib import Path
import psutil
import os

from core.config import Config
from core.database import Database
from core.observability import ObservabilityTracker
from helpers.logger import (
    print_phase_start,
    print_phase_complete,
    print_checkmark,
    ProgressBar,
    format_duration,
    get_system_info,
)
from helpers.rickbot import START_SUCCESS_RICKBOT_ART
from termcolor import colored

logger = logging.getLogger(__name__)


class RickBot(commands.Bot):
    """Production-grade Discord bot with database observability"""

    def __init__(self, config: Config):
        """
        Initialize RickBot.

        Args:
            config: Validated configuration instance
        """
        # Build intents from config
        intents = self._build_intents(config.intents)

        super().__init__(
            command_prefix=commands.when_mentioned,  # Fallback only (not used)
            intents=intents,
            application_id=config.bot.application_id,
            owner_ids=set(config.bot.owner_ids) if config.bot.owner_ids else None,
            chunk_guilds_at_startup=False,  # Performance optimization
        )

        self.config = config
        self.start_time: Optional[float] = None
        self.db: Optional[Database] = None
        self.observer: Optional[ObservabilityTracker] = None

    @staticmethod
    def _build_intents(intent_config) -> discord.Intents:
        """
        Build Discord intents from config.

        Args:
            intent_config: IntentsConfig instance

        Returns:
            discord.Intents object
        """
        intents = discord.Intents.none()
        for intent_name, enabled in intent_config.model_dump().items():
            if enabled:
                setattr(intents, intent_name, True)
        return intents

    async def setup_hook(self) -> None:
        """Initialize bot before login (runs once)"""
        print_phase_start("Bot Setup")

        # Connect to MongoDB
        start_time = time.time()
        await self._setup_database()
        print_phase_complete("Database connection", time.time() - start_time)

        # Initialize observability tracker
        start_time = time.time()
        self.observer = ObservabilityTracker(self.db, self.config.observability)
        print_checkmark(
            "Observability tracker initialized",
            success=True,
            duration=time.time() - start_time,
        )

        # Set up app_command hooks for tracking
        self._setup_command_tracking()
        print_checkmark("Command tracking hooks configured", success=True)

        # Load cogs
        await self._load_cogs()

        # Sync commands
        if self.config.bot.sync_commands_on_ready:
            await self._sync_commands()

        # Start metric aggregation task
        if self.config.observability.aggregate_metrics_interval > 0:
            self.metric_snapshot_task.change_interval(
                seconds=self.config.observability.aggregate_metrics_interval
            )
            self.metric_snapshot_task.start()
            print_checkmark("Metric aggregation task started", success=True)

        print()

    async def _setup_database(self) -> None:
        """Initialize MongoDB connection with retry logic"""
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Connecting to MongoDB (attempt {attempt}/{max_retries})..."
                )

                client = AsyncIOMotorClient(
                    self.config.mongodb.uri,
                    maxPoolSize=self.config.mongodb.pool_size,
                    serverSelectionTimeoutMS=self.config.mongodb.timeout_ms,
                    retryWrites=self.config.mongodb.retry_writes,
                )

                # Test connection
                await client.admin.command("ping")

                self.db = Database(client, self.config.mongodb)
                await self.db.ensure_indexes()

                logger.info("Successfully connected to MongoDB")
                return

            except Exception as e:
                logger.error(
                    f"MongoDB connection failed (attempt {attempt}/{max_retries}): {e}"
                )

                if attempt == max_retries:
                    logger.critical("Failed to connect to MongoDB after all retries")
                    raise

                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

    def _setup_command_tracking(self) -> None:
        """Set up hooks to track all command executions"""
        # Store original _call method
        original_call = self.tree._call

        async def tracked_call(interaction: discord.Interaction):
            """Wrap command execution with tracking"""
            start_time = time.time()
            error_ref = None
            success = True

            try:
                await original_call(interaction)
            except Exception as e:
                success = False

                # Log error and get reference
                error_ref = await self.observer.log_error(
                    e,
                    interaction=interaction,
                    command_name=(
                        interaction.command.qualified_name
                        if interaction.command
                        else None
                    ),
                )

                # Show error to user
                await self._show_error_to_user(interaction, error_ref)

                # Log but don't re-raise - we've handled it
                logger.error(f"Command error {error_ref}: {e}", exc_info=True)
            finally:
                # Always log execution
                execution_time = (time.time() - start_time) * 1000  # milliseconds

                if interaction.command:
                    # Extract arguments if configured
                    arguments = None
                    if self.config.observability.track_command_args:
                        if hasattr(interaction, "namespace"):
                            arguments = {
                                name: value
                                for name, value in interaction.namespace.__dict__.items()
                                if not name.startswith("_")
                            }

                    await self.observer.log_command_execution(
                        command=interaction.command,
                        interaction=interaction,
                        execution_time_ms=execution_time,
                        success=success,
                        error_reference=error_ref,
                        arguments=arguments,
                    )

                    # Log slow commands
                    if execution_time > 3000:  # > 3 seconds
                        logger.warning(
                            f"Slow command: {interaction.command.qualified_name} "
                            f"took {execution_time:.0f}ms"
                        )

        # Replace the _call method
        self.tree._call = tracked_call

    async def _show_error_to_user(
        self, interaction: discord.Interaction, error_ref: str
    ) -> None:
        """
        Show user-friendly error message with reference code.

        Args:
            interaction: Discord interaction
            error_ref: Error reference code
        """
        embed = discord.Embed(
            title="⚠️ An Error Occurred",
            description=(
                "Something went wrong while processing your command.\n\n"
                f"**Error Reference:** `{error_ref}`\n\n"
                "If this issue persists, please contact support with this reference code."
            ),
            color=discord.Color.red(),
        )

        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            # Failsafe if we can't even send the error message
            logger.error(f"Could not send error message to user for {error_ref}: {e}")

    async def _load_cogs(self) -> None:
        """Load all cogs from cogs directory"""
        cogs_path = Path("cogs")
        if not cogs_path.exists():
            logger.warning("No cogs directory found, skipping cog loading")
            return

        # Collect all cog files first
        cog_files = [
            cog_file
            for cog_file in cogs_path.rglob("*.py")
            if not cog_file.name.startswith("_")
        ]

        if not cog_files:
            print_checkmark("No cogs found to load", success=True)
            return

        print_phase_start(f"Loading Cogs ({len(cog_files)} found)")

        loaded_count = 0
        failed_count = 0
        start_time = time.time()

        # Create progress bar
        progress = ProgressBar(total=len(cog_files), prefix="  ")

        for i, cog_file in enumerate(cog_files):
            # Convert path to module notation
            module_path = (
                str(cog_file.with_suffix("")).replace("/", ".").replace("\\", ".")
            )

            try:
                await self.load_extension(module_path)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load cog {module_path}: {e}", exc_info=True)
                failed_count += 1

            # Update progress bar
            progress.update(i + 1)

        # Show summary
        duration = time.time() - start_time
        if failed_count == 0:
            print_checkmark(
                f"All {loaded_count} cogs loaded successfully",
                success=True,
                duration=duration,
            )
        else:
            print_checkmark(
                f"{loaded_count} cogs loaded, {failed_count} failed",
                success=failed_count == 0,
                duration=duration,
            )

    async def _sync_commands(self) -> None:
        """Sync slash commands to Discord"""
        print_phase_start("Syncing Commands")
        start_time = time.time()

        if self.config.bot.dev_guild_id:
            # Sync to dev guild (instant)
            guild = discord.Object(self.config.bot.dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print_checkmark(
                f"Commands synced to dev guild {self.config.bot.dev_guild_id}",
                success=True,
                duration=time.time() - start_time,
            )
        else:
            # Sync globally (takes up to 1 hour)
            await self.tree.sync()
            print_checkmark(
                "Commands synced globally (may take up to 1 hour to propagate)",
                success=True,
                duration=time.time() - start_time,
            )

    @tasks.loop(seconds=300)  # Default 5 minutes, overridden in setup_hook
    async def metric_snapshot_task(self) -> None:
        """Periodically save metric snapshots to database"""
        try:
            # Approximate user count from cached guilds
            user_count = sum(g.member_count or 0 for g in self.guilds)

            # Get memory usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024

            await self.observer.create_metric_snapshot(
                guild_count=len(self.guilds),
                user_count=user_count,
                uptime_seconds=self.get_uptime(),
                memory_mb=memory_mb,
            )

            logger.debug(
                f"Created metric snapshot: {len(self.guilds)} guilds, {memory_mb:.1f}MB memory"
            )
        except Exception as e:
            logger.error(f"Failed to create metric snapshot: {e}")

    @metric_snapshot_task.before_loop
    async def before_metric_snapshot(self) -> None:
        """Wait for bot to be ready before starting metrics"""
        await self.wait_until_ready()

    async def on_ready(self) -> None:
        """Bot is ready (can be called multiple times on reconnect)"""
        if self.start_time is None:
            # First time ready
            self.start_time = time.time()

            # Print the beautiful ASCII art
            print()
            print(START_SUCCESS_RICKBOT_ART)

            # Get system info
            sys_info = get_system_info()
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024

            # Display info directly under the art
            print(
                f"  {colored('Bot User:', 'cyan')} {colored(str(self.user), 'white', attrs=['bold'])} {colored(f'(ID: {self.user.id})', 'dark_grey')}"
            )
            print(
                f"  {colored('Guilds:', 'cyan')} {colored(str(len(self.guilds)), 'white', attrs=['bold'])}"
            )
            print(
                f"  {colored('Discord.py:', 'cyan')} {colored(discord.__version__, 'white', attrs=['bold'])}"
            )
            print(
                f"  {colored('Platform:', 'cyan')} {colored(sys_info['platform'], 'white', attrs=['bold'])}"
            )
            print(
                f"  {colored('Memory:', 'cyan')} {colored(f'{memory_mb:.1f} MB', 'white', attrs=['bold'])}"
            )
            print()

            # Set status
            await self._set_status()
        else:
            # Reconnected
            logger.info(f"Bot reconnected as {self.user}")

    async def _set_status(self) -> None:
        """Set bot status from config"""
        activity = None

        if self.config.bot.status_type == "playing":
            activity = discord.Game(name=self.config.bot.status_text)
        elif self.config.bot.status_type in ("watching", "listening", "competing"):
            activity_type = getattr(discord.ActivityType, self.config.bot.status_type)
            activity = discord.Activity(
                type=activity_type, name=self.config.bot.status_text
            )

        if activity:
            await self.change_presence(activity=activity)

    async def close(self) -> None:
        """Graceful shutdown with cleanup"""
        print()
        print_phase_start("Bot Shutdown")

        # Stop metric task
        if self.metric_snapshot_task.is_running():
            self.metric_snapshot_task.cancel()
            print_checkmark("Metric aggregation task stopped", success=True)

        # Final metric snapshot
        if self.observer and self.db:
            try:
                user_count = sum(g.member_count or 0 for g in self.guilds)
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024

                await self.observer.create_metric_snapshot(
                    guild_count=len(self.guilds),
                    user_count=user_count,
                    uptime_seconds=self.get_uptime(),
                    memory_mb=memory_mb,
                )
                print_checkmark("Final metric snapshot saved", success=True)
            except Exception as e:
                print_checkmark(
                    f"Failed to save final metric snapshot: {e}", success=False
                )
                logger.error(f"Failed to save final metric snapshot: {e}")

        # Close MongoDB connection
        if self.db:
            await self.db.close()
            print_checkmark("Database connection closed", success=True)

        # Close bot connection
        await super().close()
        print_checkmark("Discord connection closed", success=True)

    def get_uptime(self) -> float:
        """
        Get bot uptime in seconds.

        Returns:
            Uptime in seconds, or 0.0 if not started
        """
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time
