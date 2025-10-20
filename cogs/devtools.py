"""
RickBot 2.0 - Dev Tools Cog

Development utilities for bot owners (hot reloading, error viewing, metrics).
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR, SUCCESS_EMBED_COLOR
from helpers.checks import is_owner
from helpers.ui import ErrorViewer

if TYPE_CHECKING:
    from core.bot import RickBot


class DevTools(commands.Cog):
    """Development utilities for bot maintenance"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

    @app_commands.command(name="reload", description="Reload a cog (hot reload)")
    @app_commands.describe(cog="Name of the cog to reload")
    @is_owner()
    async def reload(self, interaction: discord.Interaction, cog: str):
        """Hot reload a cog without restarting the bot"""
        try:
            await self.bot.reload_extension(cog)
            embed = discord.Embed(
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded `{cog}`",
                color=SUCCESS_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except commands.ExtensionNotLoaded:
            # Try to load it if not loaded
            try:
                await self.bot.load_extension(cog)
                embed = discord.Embed(
                    title="✅ Cog Loaded",
                    description=f"Cog `{cog}` wasn't loaded, so I loaded it for you!",
                    color=SUCCESS_EMBED_COLOR,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Load Failed",
                    description=f"```python\n{str(e)}\n```",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"```python\n{str(e)}\n```",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @reload.autocomplete("cog")
    async def reload_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete for loaded cogs"""
        cogs = list(self.bot.extensions.keys())
        return [
            app_commands.Choice(name=cog, value=cog)
            for cog in cogs
            if current.lower() in cog.lower()
        ][:25]

    @app_commands.command(name="sync", description="Sync slash commands")
    @app_commands.describe(guild_id="Guild ID to sync to (leave empty for global sync)")
    @is_owner()
    async def sync(
        self, interaction: discord.Interaction, guild_id: Optional[str] = None
    ):
        """Manually sync slash commands"""
        await interaction.response.defer(ephemeral=True)

        try:
            if guild_id:
                # Sync to specific guild
                guild = discord.Object(id=int(guild_id))
                self.bot.tree.copy_global_to(guild=guild)
                await self.bot.tree.sync(guild=guild)
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description=f"Synced commands to guild `{guild_id}`",
                    color=SUCCESS_EMBED_COLOR,
                )
            else:
                # Global sync
                await self.bot.tree.sync()
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description="Synced commands globally (may take up to 1 hour)",
                    color=SUCCESS_EMBED_COLOR,
                )

            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"```python\n{str(e)}\n```",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="errors", description="View recent errors from database")
    @app_commands.describe(
        limit="Number of errors to fetch (default: 10)",
        unresolved_only="Show only unresolved errors",
    )
    @is_owner()
    async def errors(
        self,
        interaction: discord.Interaction,
        limit: int = 10,
        unresolved_only: bool = False,
    ):
        """View errors logged in the database"""
        await interaction.response.defer(ephemeral=True)

        # Build filter
        filter_query = {"resolved": False} if unresolved_only else {}

        # Fetch errors
        errors = await self.bot.db.error_logs.find_many(
            filter=filter_query,
            limit=min(limit, 50),  # Cap at 50
            sort=[("occurred_at", -1)],
        )

        if not errors:
            await interaction.followup.send(
                (
                    "✅ No errors found!"
                    if unresolved_only
                    else "✅ No errors logged yet!"
                ),
                ephemeral=True,
            )
            return

        # Create error viewer
        viewer = ErrorViewer(errors=errors, db=self.bot.db)
        embed = viewer._build_error_embed()

        await interaction.followup.send(embed=embed, view=viewer, ephemeral=True)

    @app_commands.command(name="metrics", description="View performance metrics")
    @is_owner()
    async def metrics(self, interaction: discord.Interaction):
        """View latest performance metrics snapshot"""
        await interaction.response.defer(ephemeral=True)

        # Get latest metric snapshot
        snapshots = await self.bot.db.metrics.find_many(
            filter={}, limit=5, sort=[("snapshot_at", -1)]
        )

        if not snapshots:
            await interaction.followup.send(
                "No metrics snapshots available yet!", ephemeral=True
            )
            return

        latest = snapshots[0]

        embed = discord.Embed(
            title="📊 Performance Metrics",
            description="Latest snapshot from database",
            color=MAIN_EMBED_COLOR,
            timestamp=latest.snapshot_at,
        )

        # Bot stats
        embed.add_field(
            name="🤖 Bot Stats",
            value=(
                f"**Guilds:** {latest.guild_count}\n"
                f"**Users:** {latest.user_count:,}\n"
                f"**Uptime:** {self._format_seconds(latest.uptime_seconds)}\n"
                f"**Memory:** {latest.memory_usage_mb:.1f} MB"
                if latest.memory_usage_mb
                else ""
            ),
            inline=True,
        )

        # Command stats
        embed.add_field(
            name="⚡ Commands",
            value=(
                f"**Total Executed:** {latest.total_commands_executed:,}\n"
                f"**Unique Commands:** {len(latest.commands_by_name)}\n"
                f"**Total Errors:** {latest.total_errors}"
            ),
            inline=True,
        )

        # Top commands
        if latest.commands_by_name:
            top_commands = sorted(
                latest.commands_by_name.items(), key=lambda x: x[1], reverse=True
            )[:5]

            top_commands_str = "\n".join(
                [f"`/{name}`: {count}" for name, count in top_commands]
            )

            embed.add_field(
                name="🔥 Top Commands", value=top_commands_str, inline=False
            )

        # Avg timing
        if latest.average_command_time_ms:
            slowest = sorted(
                latest.average_command_time_ms.items(), key=lambda x: x[1], reverse=True
            )[:3]

            timing_str = "\n".join(
                [f"`/{name}`: {time:.1f}ms" for name, time in slowest]
            )

            embed.add_field(name="🐌 Slowest Commands", value=timing_str, inline=False)

        embed.set_footer(text=f"{len(snapshots)} snapshots in database")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="dbstats", description="View database statistics")
    @is_owner()
    async def dbstats(self, interaction: discord.Interaction):
        """View MongoDB collection statistics"""
        await interaction.response.defer(ephemeral=True)

        # Count documents in each collection
        command_count = await self.bot.db.command_logs.count()
        error_count = await self.bot.db.error_logs.count()
        metric_count = await self.bot.db.metrics.count()
        guild_count = await self.bot.db.guild_settings.count()

        embed = discord.Embed(
            title="💾 Database Statistics",
            description=f"MongoDB Database: `{self.bot.config.mongodb.database}`",
            color=MAIN_EMBED_COLOR,
        )

        embed.add_field(
            name="📊 Collections",
            value=(
                f"**Command Logs:** {command_count:,}\n"
                f"**Error Logs:** {error_count:,}\n"
                f"**Metrics:** {metric_count:,}\n"
                f"**Guild Settings:** {guild_count:,}"
            ),
            inline=False,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    def _format_seconds(self, seconds: float) -> str:
        """Format seconds as human-readable string"""
        seconds = int(seconds)
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        return " ".join(parts)


async def setup(bot: "RickBot"):
    """Load the DevTools cog"""
    await bot.add_cog(DevTools(bot))
