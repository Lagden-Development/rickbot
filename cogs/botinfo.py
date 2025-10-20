"""
RickBot 2.0 - Bot Info Cog

Essential bot information commands with database-powered statistics.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING
from datetime import datetime, timezone

from helpers.colors import MAIN_EMBED_COLOR, SUCCESS_EMBED_COLOR
from helpers.ui import PaginatedView

if TYPE_CHECKING:
    from core.bot import RickBot


class BotInfo(commands.Cog):
    """Essential bot information and statistics commands"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot's latency to Discord"""
        latency_ms = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency_ms}ms**",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.set_footer(text=f"Requested by {interaction.user}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="View bot information")
    async def info(self, interaction: discord.Interaction):
        """Display bot information and stats"""
        # Get total command count from database
        total_commands = await self.bot.db.command_logs.count()

        # Get total error count
        total_errors = await self.bot.db.error_logs.count()

        # Get bot owner
        app_info = await self.bot.application_info()
        owner = app_info.owner

        embed = discord.Embed(
            title=f"{self.bot.user.name} Information",
            description="Production-grade Discord bot framework built with RickBot 2.0",
            color=MAIN_EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )

        # Bot stats
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Guilds:** {len(self.bot.guilds)}\n"
                f"**Users:** {sum(g.member_count or 0 for g in self.bot.guilds):,}\n"
                f"**Commands Executed:** {total_commands:,}\n"
                f"**Errors Logged:** {total_errors:,}"
            ),
            inline=True,
        )

        # Technical info
        embed.add_field(
            name="⚙️ Technical",
            value=(
                f"**Uptime:** {self._format_uptime()}\n"
                f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                f"**Slash Commands:** {len(self.bot.tree.get_commands())}\n"
                f"**Cogs Loaded:** {len(self.bot.cogs)}"
            ),
            inline=True,
        )

        # Bot info
        embed.add_field(
            name="ℹ️ Information",
            value=(
                f"**Owner:** {owner.mention}\n"
                f"**Framework:** RickBot 2.0\n"
                f"**Database:** MongoDB\n"
                f"**Python:** discord.py {discord.__version__}"
            ),
            inline=False,
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="View detailed bot statistics")
    @app_commands.describe(limit="Number of commands to show (default: 10)")
    async def stats(self, interaction: discord.Interaction, limit: int = 10):
        """View detailed command usage statistics from database"""
        # Validate limit
        if limit < 1 or limit > 50:
            await interaction.response.send_message(
                "❌ Limit must be between 1 and 50!", ephemeral=True
            )
            return

        # Defer response as this might take a moment
        await interaction.response.defer()

        # Aggregate command usage
        pipeline = [
            {
                "$group": {
                    "_id": "$command_name",
                    "count": {"$sum": 1},
                    "avg_time": {"$avg": "$execution_time_ms"},
                    "success_rate": {"$avg": {"$cond": ["$success", 1, 0]}},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]

        stats = await self.bot.db.command_logs.aggregate(pipeline)

        if not stats:
            await interaction.followup.send(
                "No command statistics available yet!", ephemeral=True
            )
            return

        # Build embed
        embed = discord.Embed(
            title="📊 Command Statistics",
            description=f"Top {len(stats)} most used commands",
            color=MAIN_EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )

        for stat in stats:
            success_rate = stat["success_rate"] * 100
            embed.add_field(
                name=f"/{stat['_id']}",
                value=(
                    f"**Uses:** {stat['count']:,}\n"
                    f"**Avg Time:** {stat['avg_time']:.1f}ms\n"
                    f"**Success:** {success_rate:.1f}%"
                ),
                inline=True,
            )

        # Add total stats
        total_commands = await self.bot.db.command_logs.count()
        embed.set_footer(text=f"Total Commands Executed: {total_commands:,}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="uptime", description="View bot uptime and performance")
    async def uptime(self, interaction: discord.Interaction):
        """Display bot uptime and performance metrics"""
        # Get latest metric snapshot
        metrics = await self.bot.db.metrics.find_many(
            filter={}, limit=1, sort=[("snapshot_at", -1)]
        )

        embed = discord.Embed(
            title="⏱️ Bot Uptime & Performance",
            color=MAIN_EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )

        # Uptime
        uptime_str = self._format_uptime()
        embed.add_field(name="Uptime", value=f"```{uptime_str}```", inline=False)

        # Latest metrics
        if metrics:
            metric = metrics[0]
            embed.add_field(
                name="📊 Latest Snapshot",
                value=(
                    f"**Guilds:** {metric.guild_count}\n"
                    f"**Users:** {metric.user_count:,}\n"
                    f"**Memory:** {metric.memory_usage_mb:.1f} MB"
                    if metric.memory_usage_mb
                    else ""
                ),
                inline=True,
            )

            embed.add_field(
                name="📈 Total Activity",
                value=(
                    f"**Commands:** {metric.total_commands_executed:,}\n"
                    f"**Errors:** {metric.total_errors}"
                ),
                inline=True,
            )

        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=embed)

    def _format_uptime(self) -> str:
        """Format bot uptime as human-readable string"""
        uptime_seconds = int(self.bot.get_uptime())

        days, remainder = divmod(uptime_seconds, 86400)
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
    """Load the BotInfo cog"""
    await bot.add_cog(BotInfo(bot))
