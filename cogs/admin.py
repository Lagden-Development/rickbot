"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Admin Cog

Moderation commands with modern UI components (modals, confirmations).
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING, Optional, Literal
from datetime import timedelta

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR, SUCCESS_EMBED_COLOR
from helpers.ui import ConfirmationView

if TYPE_CHECKING:
    from core.bot import RickBot


class ReasonModal(discord.ui.Modal, title="Moderation Reason"):
    """Modal for collecting moderation action reason"""

    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Enter reason for this action...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500,
    )

    def __init__(self, action_type: str):
        super().__init__(title=f"{action_type} - Reason")
        self.submitted_reason: Optional[str] = None

    async def on_submit(self, interaction: discord.Interaction):
        self.submitted_reason = self.reason.value or "No reason provided"
        await interaction.response.defer()


class BanModal(discord.ui.Modal, title="Ban Member"):
    """Modal for collecting ban reason and duration"""

    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Enter reason for ban...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500,
    )

    delete_days = discord.ui.TextInput(
        label="Delete Message History (days)",
        placeholder="0-7 days (default: 0)",
        style=discord.TextStyle.short,
        required=False,
        default="0",
        max_length=1,
    )

    def __init__(self):
        super().__init__(title="Ban Member")
        self.submitted_reason: Optional[str] = None
        self.submitted_delete_days: int = 0

    async def on_submit(self, interaction: discord.Interaction):
        self.submitted_reason = self.reason.value or "No reason provided"

        # Validate delete_days
        try:
            days = int(self.delete_days.value) if self.delete_days.value else 0
            self.submitted_delete_days = max(0, min(7, days))
        except ValueError:
            self.submitted_delete_days = 0

        await interaction.response.defer()


class Admin(commands.Cog):
    """Server moderation and management commands"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="The member to kick")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        """Kick a member with modal reason collection"""
        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to kick members!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check role hierarchy
        if member.top_role >= interaction.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description=f"I cannot kick {member.mention} - their role is higher than or equal to mine!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check if trying to kick bot owner
        if member.id == interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ Cannot Kick Owner",
                description="I cannot kick the server owner!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Show reason modal
        modal = ReasonModal("Kick")
        await interaction.response.send_modal(modal)

        # Wait for modal submission
        if await modal.wait():
            return  # Timeout

        reason = modal.submitted_reason

        try:
            # Try to DM the member
            try:
                dm_embed = discord.Embed(
                    title="🚪 You were kicked",
                    description=f"You were kicked from **{interaction.guild.name}**",
                    color=ERROR_EMBED_COLOR,
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(
                    name="Moderator", value=str(interaction.user), inline=False
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # Can't DM user

            # Kick the member
            await member.kick(reason=f"{interaction.user} | {reason}")

            # Send success message
            embed = discord.Embed(
                title="✅ Member Kicked",
                description=f"Successfully kicked {member.mention}",
                color=SUCCESS_EMBED_COLOR,
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )

            await interaction.followup.send(embed=embed, ephemeral=False)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Kick Failed",
                description="I don't have permission to kick this member!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Kick Failed",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban", user_id="User ID to ban (if not in server)"
    )
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None,
        user_id: Optional[str] = None,
    ):
        """Ban a member or user with modal reason collection"""
        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to ban members!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Determine target
        target: Optional[discord.User | discord.Member] = None

        if member:
            target = member

            # Check role hierarchy
            if (
                isinstance(target, discord.Member)
                and target.top_role >= interaction.guild.me.top_role
            ):
                embed = discord.Embed(
                    title="❌ Role Hierarchy Error",
                    description=f"I cannot ban {target.mention} - their role is higher than or equal to mine!",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Check if trying to ban bot owner
            if target.id == interaction.guild.owner_id:
                embed = discord.Embed(
                    title="❌ Cannot Ban Owner",
                    description="I cannot ban the server owner!",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        elif user_id:
            try:
                target = await self.bot.fetch_user(int(user_id))
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid User ID",
                    description="Please provide a valid user ID!",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            except discord.NotFound:
                embed = discord.Embed(
                    title="❌ User Not Found",
                    description="Could not find a user with that ID!",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        else:
            embed = discord.Embed(
                title="❌ No Target Specified",
                description="Please specify either a member or user ID!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Show ban modal
        modal = BanModal()
        await interaction.response.send_modal(modal)

        # Wait for modal submission
        if await modal.wait():
            return  # Timeout

        reason = modal.submitted_reason
        delete_days = modal.submitted_delete_days

        try:
            # Try to DM the user
            if isinstance(target, discord.Member):
                try:
                    dm_embed = discord.Embed(
                        title="🔨 You were banned",
                        description=f"You were banned from **{interaction.guild.name}**",
                        color=ERROR_EMBED_COLOR,
                    )
                    dm_embed.add_field(name="Reason", value=reason, inline=False)
                    dm_embed.add_field(
                        name="Moderator", value=str(interaction.user), inline=False
                    )
                    await target.send(embed=dm_embed)
                except discord.Forbidden:
                    pass  # Can't DM user

            # Ban the user
            await interaction.guild.ban(
                target,
                reason=f"{interaction.user} | {reason}",
                delete_message_seconds=delete_days * 86400,  # Convert days to seconds
            )

            # Send success message
            embed = discord.Embed(
                title="✅ User Banned",
                description=f"Successfully banned {target.mention} ({target.id})",
                color=SUCCESS_EMBED_COLOR,
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(
                name="Message History Deleted", value=f"{delete_days} days", inline=True
            )

            await interaction.followup.send(embed=embed, ephemeral=False)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Ban Failed",
                description="I don't have permission to ban this user!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Ban Failed",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(user_id="User ID to unban")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(self, interaction: discord.Interaction, user_id: str):
        """Unban a user by their ID"""
        await interaction.response.defer(ephemeral=False)

        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to unban members!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            # Parse user ID
            try:
                user_id_int = int(user_id)
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid User ID",
                    description="Please provide a valid user ID!",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Check if user is banned
            try:
                ban_entry = await interaction.guild.fetch_ban(
                    discord.Object(id=user_id_int)
                )
                user = ban_entry.user
            except discord.NotFound:
                embed = discord.Embed(
                    title="❌ User Not Banned",
                    description="This user is not banned!",
                    color=ERROR_EMBED_COLOR,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Unban the user
            await interaction.guild.unban(
                user, reason=f"Unbanned by {interaction.user}"
            )

            # Send success message
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"Successfully unbanned {user.mention} ({user.id})",
                color=SUCCESS_EMBED_COLOR,
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )

            await interaction.followup.send(embed=embed, ephemeral=False)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Unban Failed",
                description="I don't have permission to unban users!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Unban Failed",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration (e.g., 10m, 1h, 1d)",
        reason="Reason for timeout",
    )
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: str,
        reason: Optional[str] = None,
    ):
        """Timeout a member for a specified duration"""
        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to timeout members!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check role hierarchy
        if member.top_role >= interaction.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description=f"I cannot timeout {member.mention} - their role is higher than or equal to mine!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Parse duration
        try:
            duration_seconds = self._parse_duration(duration)
            if duration_seconds is None or duration_seconds < 60:
                raise ValueError("Duration must be at least 1 minute")
            if duration_seconds > 2419200:  # 28 days max
                raise ValueError("Duration cannot exceed 28 days")

            timeout_delta = timedelta(seconds=duration_seconds)
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description=f"{str(e)}\n\nExamples: `10m`, `1h`, `2d`",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        reason = reason or "No reason provided"

        try:
            # Apply timeout
            await member.timeout(timeout_delta, reason=f"{interaction.user} | {reason}")

            # Send success message
            embed = discord.Embed(
                title="✅ Member Timed Out",
                description=f"Successfully timed out {member.mention}",
                color=SUCCESS_EMBED_COLOR,
            )
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Timeout Failed",
                description="I don't have permission to timeout this member!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Timeout Failed",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="untimeout", description="Remove timeout from a member")
    @app_commands.describe(member="The member to remove timeout from")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        """Remove timeout from a member"""
        # Check if bot has permissions
        if not interaction.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to remove timeouts!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check if member is timed out
        if not member.is_timed_out():
            embed = discord.Embed(
                title="❌ Not Timed Out",
                description=f"{member.mention} is not timed out!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Remove timeout
            await member.timeout(None, reason=f"Timeout removed by {interaction.user}")

            # Send success message
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"Successfully removed timeout from {member.mention}",
                color=SUCCESS_EMBED_COLOR,
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Failed to Remove Timeout",
                description="I don't have permission to remove timeouts!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Failed to Remove Timeout",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        member="Only delete messages from this member",
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: int,
        member: Optional[discord.Member] = None,
    ):
        """Delete multiple messages with confirmation"""
        # Check if bot has permissions
        if not interaction.channel.permissions_for(
            interaction.guild.me
        ).manage_messages:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to delete messages in this channel!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Validate amount
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number between 1 and 100!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create confirmation view
        confirmation_text = f"delete {amount} messages"
        if member:
            confirmation_text += f" from {member.mention}"
        confirmation_text += "?"

        embed = discord.Embed(
            title="⚠️ Confirm Purge",
            description=f"Are you sure you want to {confirmation_text}",
            color=MAIN_EMBED_COLOR,
        )

        view = ConfirmationView(
            author_id=interaction.user.id, confirm_label="Delete", cancel_label="Cancel"
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        # Wait for confirmation
        await view.wait()

        if view.value is None:
            # Timeout
            embed = discord.Embed(
                title="⏱️ Purge Cancelled",
                description="Confirmation timed out.",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.edit_original_response(embed=embed, view=None)
            return

        if not view.value:
            # Cancelled
            embed = discord.Embed(
                title="❌ Purge Cancelled",
                description="Purge operation cancelled.",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.edit_original_response(embed=embed, view=None)
            return

        # Perform purge
        try:

            def check(m):
                if member:
                    return m.author.id == member.id
                return True

            deleted = await interaction.channel.purge(limit=amount, check=check)

            # Send success message
            embed = discord.Embed(
                title="✅ Messages Deleted",
                description=f"Successfully deleted {len(deleted)} messages!",
                color=SUCCESS_EMBED_COLOR,
            )
            if member:
                embed.add_field(name="Target", value=member.mention, inline=True)
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )

            await interaction.edit_original_response(embed=embed, view=None)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Purge Failed",
                description="I don't have permission to delete messages!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.edit_original_response(embed=embed, view=None)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Purge Failed",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.guild_only()
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        """Set channel slowmode delay"""
        # Check if bot has permissions
        if not interaction.channel.permissions_for(
            interaction.guild.me
        ).manage_channels:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to manage this channel!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Validate seconds
        if seconds < 0 or seconds > 21600:  # Max 6 hours
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Slowmode must be between 0 and 21600 seconds (6 hours)!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await interaction.channel.edit(slowmode_delay=seconds)

            if seconds == 0:
                description = "Slowmode has been disabled!"
            else:
                description = f"Slowmode set to {seconds} seconds"

            embed = discord.Embed(
                title="✅ Slowmode Updated",
                description=description,
                color=SUCCESS_EMBED_COLOR,
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(
                name="Channel", value=interaction.channel.mention, inline=True
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Slowmode Failed",
                description="I don't have permission to manage this channel!",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Slowmode Failed",
                description=f"An error occurred: {str(e)}",
                color=ERROR_EMBED_COLOR,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    def _parse_duration(self, duration: str) -> Optional[int]:
        """
        Parse duration string to seconds.

        Supports: 10s, 5m, 1h, 2d
        """
        duration = duration.strip().lower()

        # Extract number and unit
        if duration[-1] in ["s", "m", "h", "d"]:
            try:
                value = int(duration[:-1])
                unit = duration[-1]
            except ValueError:
                return None
        else:
            return None

        # Convert to seconds
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}

        return value * multipliers.get(unit, 0)


async def setup(bot: "RickBot"):
    """Load the Admin cog"""
    await bot.add_cog(Admin(bot))
