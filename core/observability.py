"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Observability System

Database-first observability: track every command, error, and metric in MongoDB.
"""

import random
import string
import traceback as tb
from typing import Optional, Any
import logging
from datetime import datetime, timezone

import discord
from discord import app_commands, Interaction

from core.models import CommandLog, ErrorLog, MetricSnapshot
from core.database import Database
from core.config import ObservabilityConfig

logger = logging.getLogger(__name__)


class ObservabilityTracker:
    """Tracks commands, errors, and metrics - all in MongoDB"""

    def __init__(self, db: Database, config: ObservabilityConfig):
        """
        Initialize observability tracker.

        Args:
            db: Database instance
            config: Observability configuration
        """
        self.db = db
        self.config = config

        # In-memory counters for metric aggregation
        self._command_counts: dict[str, int] = {}
        self._command_timings: dict[str, list[float]] = {}
        self._error_counts: dict[str, int] = {}

    async def generate_error_reference(self) -> str:
        """
        Generate unique error reference code with collision detection.

        Returns:
            Error reference string (e.g., "ERR-A7K9X2")
        """
        chars = string.ascii_uppercase + string.digits
        max_attempts = 3

        for attempt in range(max_attempts):
            code = "".join(random.choices(chars, k=self.config.error_reference_length))
            error_ref = f"ERR-{code}"

            # Check for collisions in database
            try:
                existing = await self.db.error_logs.collection.find_one(
                    {"error_reference": error_ref}
                )
                if not existing:
                    return error_ref
                else:
                    logger.warning(
                        f"Error reference collision detected: {error_ref} (attempt {attempt + 1}/{max_attempts})"
                    )
            except Exception as e:
                logger.error(f"Failed to check error reference uniqueness: {e}")
                # Return anyway - collision is unlikely
                return error_ref

        # If all attempts failed, append timestamp to ensure uniqueness
        code = "".join(random.choices(chars, k=self.config.error_reference_length))
        timestamp_suffix = str(int(datetime.now(timezone.utc).timestamp()))[-3:]
        error_ref = f"ERR-{code}{timestamp_suffix}"
        logger.warning(f"Using timestamp-enhanced error reference: {error_ref}")
        return error_ref

    async def log_command_execution(
        self,
        command: discord.app_commands.Command | discord.app_commands.ContextMenu,
        interaction: Interaction,
        execution_time_ms: float,
        success: bool,
        error_reference: Optional[str] = None,
        arguments: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log command execution to database.

        Args:
            command: The command that was executed
            interaction: Discord interaction
            execution_time_ms: How long the command took in milliseconds
            success: Whether the command succeeded
            error_reference: Error reference if failed
            arguments: Command arguments (if tracking enabled)
        """
        if not self.config.track_command_execution:
            return

        # Determine command type
        if isinstance(command, discord.app_commands.ContextMenu):
            cmd_type = (
                "context_menu_user"
                if command.type == discord.AppCommandType.user
                else "context_menu_message"
            )
        else:
            cmd_type = "slash"

        # Build command log
        log = CommandLog(
            command_name=command.qualified_name,
            command_type=cmd_type,
            execution_time_ms=execution_time_ms,
            success=success,
            user_id=interaction.user.id,
            user_name=str(interaction.user),
            guild_id=interaction.guild_id,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=(
                interaction.channel.name
                if interaction.channel and hasattr(interaction.channel, "name")
                else None
            ),
            arguments=arguments if self.config.track_command_args else None,
            error_reference=error_reference,
        )

        try:
            await self.db.command_logs.insert_one(log)
        except Exception as e:
            logger.error(f"Failed to log command execution: {e}")

        # Update in-memory counters for metrics
        self._command_counts[command.qualified_name] = (
            self._command_counts.get(command.qualified_name, 0) + 1
        )

        if self.config.track_command_timing:
            if command.qualified_name not in self._command_timings:
                self._command_timings[command.qualified_name] = []
            self._command_timings[command.qualified_name].append(execution_time_ms)

    async def log_error(
        self,
        error: Exception,
        interaction: Optional[Interaction] = None,
        command_name: Optional[str] = None,
        additional_context: Optional[dict] = None,
    ) -> str:
        """
        Log error to database and return error reference.

        Args:
            error: The exception that occurred
            interaction: Discord interaction (if applicable)
            command_name: Name of the command that failed
            additional_context: Extra context data

        Returns:
            Error reference code (e.g., "ERR-A7K9X2")
        """
        error_ref = await self.generate_error_reference()

        if not self.config.track_errors:
            # Still return reference but don't store
            return error_ref

        # Build error log
        error_log = ErrorLog(
            error_reference=error_ref,
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=tb.format_exc() if self.config.store_error_traceback else None,
            command_name=command_name,
            guild_id=interaction.guild_id if interaction else None,
            channel_id=interaction.channel_id if interaction else None,
            user_id=interaction.user.id if interaction else None,
            interaction_data=additional_context,
        )

        try:
            await self.db.error_logs.insert_one(error_log)
            logger.info(f"Error logged with reference: {error_ref}")
        except Exception as e:
            logger.error(f"Failed to log error {error_ref}: {e}")

        # Update error counters for metrics
        self._error_counts[type(error).__name__] = (
            self._error_counts.get(type(error).__name__, 0) + 1
        )

        return error_ref

    async def create_metric_snapshot(
        self,
        guild_count: int,
        user_count: int,
        uptime_seconds: float,
        memory_mb: Optional[float] = None,
    ) -> None:
        """
        Create a metric snapshot for trend analysis and clean up memory.

        Args:
            guild_count: Number of guilds
            user_count: Approximate number of users
            uptime_seconds: Bot uptime in seconds
            memory_mb: Memory usage in megabytes (optional)
        """
        # Calculate average command timings
        avg_timings = {}
        for cmd, timings in self._command_timings.items():
            if timings:
                avg_timings[cmd] = sum(timings) / len(timings)

        snapshot = MetricSnapshot(
            guild_count=guild_count,
            user_count=user_count,
            uptime_seconds=uptime_seconds,
            total_commands_executed=sum(self._command_counts.values()),
            commands_by_name=dict(self._command_counts),
            average_command_time_ms=avg_timings,
            total_errors=sum(self._error_counts.values()),
            errors_by_type=dict(self._error_counts),
            memory_usage_mb=memory_mb,
        )

        try:
            await self.db.metrics.insert_one(snapshot)
            logger.debug("Created metric snapshot")

            # Clean up memory after successful snapshot
            self.cleanup_memory()

        except Exception as e:
            logger.error(f"Failed to create metric snapshot: {e}")

    def cleanup_memory(self) -> None:
        """
        Clean up in-memory metrics to prevent memory bloat.

        Called automatically after successful metric snapshots.
        Keeps only recent timing data for active monitoring.
        """
        # Clear old timing data after snapshot
        # Keep only the last 100 timings per command for short-term monitoring
        commands_to_clean = []
        for cmd, timings in self._command_timings.items():
            if len(timings) > 100:
                self._command_timings[cmd] = timings[-100:]
                commands_to_clean.append(cmd)

        if commands_to_clean:
            logger.debug(f"Cleaned timing data for {len(commands_to_clean)} commands")

        # Log memory usage stats
        total_timings = sum(len(timings) for timings in self._command_timings.values())
        logger.debug(
            f"Memory stats: {len(self._command_counts)} commands tracked, "
            f"{total_timings} timing entries, {len(self._error_counts)} error types"
        )

    def reset_metrics(self) -> None:
        """
        Completely reset all in-memory metric counters.

        WARNING: This will clear all accumulated data. Use cleanup_memory() instead
        for regular maintenance, which preserves recent data for monitoring.
        """
        self._command_counts.clear()
        self._command_timings.clear()
        self._error_counts.clear()
        logger.info("All metric counters reset")
