"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Context Menu Examples Cog

Demonstrates user and message context menus (right-click commands).
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING
from datetime import datetime, timezone

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR, SUCCESS_EMBED_COLOR

if TYPE_CHECKING:
    from core.bot import RickBot


class ContextMenuExamples(commands.Cog):
    """Context menu (right-click) command examples"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

        # Create context menu commands
        self.user_info_menu = app_commands.ContextMenu(
            name="User Info", callback=self.user_info_callback
        )

        self.avatar_menu = app_commands.ContextMenu(
            name="Get Avatar", callback=self.avatar_callback
        )

        self.quote_menu = app_commands.ContextMenu(
            name="Quote Message", callback=self.quote_callback
        )

        self.analyze_menu = app_commands.ContextMenu(
            name="Analyze Message", callback=self.analyze_callback
        )

        self.translate_menu = app_commands.ContextMenu(
            name="Translate", callback=self.translate_callback
        )

        # Add context menus to command tree
        self.bot.tree.add_command(self.user_info_menu)
        self.bot.tree.add_command(self.avatar_menu)
        self.bot.tree.add_command(self.quote_menu)
        self.bot.tree.add_command(self.analyze_menu)
        self.bot.tree.add_command(self.translate_menu)

    async def cog_unload(self) -> None:
        """Remove context menus when cog is unloaded"""
        self.bot.tree.remove_command(
            self.user_info_menu.name, type=self.user_info_menu.type
        )
        self.bot.tree.remove_command(self.avatar_menu.name, type=self.avatar_menu.type)
        self.bot.tree.remove_command(self.quote_menu.name, type=self.quote_menu.type)
        self.bot.tree.remove_command(
            self.analyze_menu.name, type=self.analyze_menu.type
        )
        self.bot.tree.remove_command(
            self.translate_menu.name, type=self.translate_menu.type
        )

    # ===========================
    # User Context Menus
    # ===========================

    async def user_info_callback(
        self, interaction: discord.Interaction, user: discord.User
    ):
        """Display detailed user information"""
        # Check if user is a member of the guild
        member = None
        if interaction.guild:
            member = interaction.guild.get_member(user.id)

        embed = discord.Embed(
            title=f"👤 User Information",
            color=MAIN_EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        # Basic info
        embed.add_field(name="Username", value=f"@{user.name}", inline=True)
        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="User ID", value=f"`{user.id}`", inline=True)

        # Account info
        embed.add_field(
            name="Created",
            value=f"<t:{int(user.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name="Bot Account", value="✅ Yes" if user.bot else "❌ No", inline=True
        )

        # Member-specific info
        if member:
            embed.add_field(
                name="Joined Server",
                value=f"<t:{int(member.joined_at.timestamp())}:R>",
                inline=True,
            )

            # Roles
            if len(member.roles) > 1:  # Exclude @everyone
                roles = [role.mention for role in reversed(member.roles[1:])][:10]
                embed.add_field(
                    name=f"Roles ({len(member.roles) - 1})",
                    value=" ".join(roles) if roles else "None",
                    inline=False,
                )

            # Key permissions
            perms = member.guild_permissions
            key_perms = []
            if perms.administrator:
                key_perms.append("Administrator")
            if perms.manage_guild:
                key_perms.append("Manage Server")
            if perms.manage_roles:
                key_perms.append("Manage Roles")
            if perms.manage_channels:
                key_perms.append("Manage Channels")
            if perms.kick_members:
                key_perms.append("Kick Members")
            if perms.ban_members:
                key_perms.append("Ban Members")

            if key_perms:
                embed.add_field(
                    name="Key Permissions", value=", ".join(key_perms), inline=False
                )

        embed.set_footer(text="Right-click → Apps → User Info")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def avatar_callback(
        self, interaction: discord.Interaction, user: discord.User
    ):
        """Get user's avatar in high resolution"""
        embed = discord.Embed(
            title=f"{user.display_name}'s Avatar", color=MAIN_EMBED_COLOR
        )

        # Get highest resolution avatar
        avatar_url = user.display_avatar.with_size(4096).url

        embed.set_image(url=avatar_url)
        embed.add_field(
            name="Download", value=f"[Click here]({avatar_url})", inline=False
        )

        embed.set_footer(text="Right-click → Apps → Get Avatar")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ===========================
    # Message Context Menus
    # ===========================

    async def quote_callback(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        """Quote a message"""
        embed = discord.Embed(
            description=message.content or "*[No text content]*",
            color=MAIN_EMBED_COLOR,
            timestamp=message.created_at,
        )

        embed.set_author(
            name=message.author.display_name, icon_url=message.author.display_avatar.url
        )

        # Add attachments info
        if message.attachments:
            attachment_text = "\n".join(
                [f"📎 [{a.filename}]({a.url})" for a in message.attachments[:5]]
            )
            embed.add_field(name="Attachments", value=attachment_text, inline=False)

        # Add embeds info
        if message.embeds:
            embed.add_field(
                name="Embeds",
                value=f"{len(message.embeds)} embed(s) in original message",
                inline=False,
            )

        # Add jump link
        embed.add_field(
            name="Source", value=f"[Jump to message]({message.jump_url})", inline=False
        )

        embed.set_footer(text=f"In #{message.channel.name}")

        await interaction.response.send_message(embed=embed)

    async def analyze_callback(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        """Analyze message statistics"""
        content = message.content

        # Calculate statistics
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        line_count = content.count("\n") + 1 if content else 0
        mention_count = len(message.mentions) + len(message.role_mentions)
        emoji_count = len(message.stickers) + content.count(
            "😀"
        )  # Simplified emoji count

        embed = discord.Embed(
            title="📊 Message Analysis",
            color=MAIN_EMBED_COLOR,
            timestamp=message.created_at,
        )

        embed.set_author(
            name=message.author.display_name, icon_url=message.author.display_avatar.url
        )

        # Statistics
        embed.add_field(
            name="Content",
            value=(
                f"**Characters:** {char_count:,}\n"
                f"**Words:** {word_count:,}\n"
                f"**Lines:** {line_count:,}"
            ),
            inline=True,
        )

        embed.add_field(
            name="Elements",
            value=(
                f"**Mentions:** {mention_count}\n"
                f"**Attachments:** {len(message.attachments)}\n"
                f"**Embeds:** {len(message.embeds)}\n"
                f"**Stickers:** {len(message.stickers)}"
            ),
            inline=True,
        )

        # Message info
        embed.add_field(
            name="Message Info",
            value=(
                f"**Channel:** {message.channel.mention}\n"
                f"**Posted:** <t:{int(message.created_at.timestamp())}:R>\n"
                f"**Edited:** {'Yes' if message.edited_at else 'No'}\n"
                f"**Pinned:** {'Yes' if message.pinned else 'No'}"
            ),
            inline=False,
        )

        # Reactions
        if message.reactions:
            reactions_text = " ".join(
                [f"{r.emoji} {r.count}" for r in message.reactions[:10]]
            )
            embed.add_field(name="Reactions", value=reactions_text, inline=False)

        embed.add_field(
            name="Jump to Message",
            value=f"[Click here]({message.jump_url})",
            inline=False,
        )

        embed.set_footer(text="Right-click → Apps → Analyze Message")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def translate_callback(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        """Simulate message translation"""
        # This is a demonstration - in production you would integrate with a translation API

        if not message.content:
            await interaction.response.send_message(
                "❌ This message has no text content to translate!", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🌐 Translation",
            description=(
                "**Original:**\n"
                f"{message.content[:500]}\n\n"
                "**Translated:** (Demo)\n"
                "*In production, this would integrate with Google Translate API or similar service.*"
            ),
            color=MAIN_EMBED_COLOR,
        )

        embed.set_author(
            name=message.author.display_name, icon_url=message.author.display_avatar.url
        )

        embed.add_field(
            name="How to Implement",
            value=(
                "1. Use Google Translate API, DeepL, or similar\n"
                "2. Detect source language automatically\n"
                "3. Translate to user's preferred language\n"
                "4. Cache results to reduce API calls\n"
                "5. Handle rate limits gracefully"
            ),
            inline=False,
        )

        embed.add_field(
            name="Source", value=f"[Jump to message]({message.jump_url})", inline=False
        )

        embed.set_footer(text="Right-click → Apps → Translate")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ===========================
    # Info Command
    # ===========================

    @app_commands.command(
        name="context_info", description="Learn about context menu commands"
    )
    async def context_info(self, interaction: discord.Interaction):
        """Information about context menu implementation"""
        embed = discord.Embed(
            title="📚 Context Menu Guide",
            description="Learn how to implement context menus (right-click commands)!",
            color=MAIN_EMBED_COLOR,
        )

        embed.add_field(
            name="What are Context Menus?",
            value=(
                "Context menus are commands that appear when you:\n"
                "• Right-click a **user** (User context menu)\n"
                "• Right-click a **message** (Message context menu)\n\n"
                "They provide quick actions without typing commands!"
            ),
            inline=False,
        )

        embed.add_field(
            name="Implementation Example",
            value=(
                "```python\n"
                "# User context menu\n"
                "user_menu = app_commands.ContextMenu(\n"
                "    name='User Info',\n"
                "    callback=self.user_info_callback\n"
                ")\n"
                "self.bot.tree.add_command(user_menu)\n\n"
                "async def user_info_callback(\n"
                "    self,\n"
                "    interaction: discord.Interaction,\n"
                "    user: discord.User\n"
                "):\n"
                "    # Handle user context menu\n"
                "    ...\n"
                "```"
            ),
            inline=False,
        )

        embed.add_field(
            name="Available Examples",
            value=(
                "**User Context Menus:**\n"
                "• User Info - Detailed user information\n"
                "• Get Avatar - High-res avatar download\n\n"
                "**Message Context Menus:**\n"
                "• Quote Message - Quote with formatting\n"
                "• Analyze Message - Message statistics\n"
                "• Translate - (Demo) Translation simulation"
            ),
            inline=False,
        )

        embed.add_field(
            name="How to Access",
            value=(
                "**Desktop:** Right-click → Apps\n"
                "**Mobile:** Long-press → Apps\n\n"
                "Context menus appear in the 'Apps' submenu!"
            ),
            inline=False,
        )

        embed.add_field(
            name="Best Practices",
            value=(
                "• Keep names short and clear (max 32 chars)\n"
                "• Use ephemeral responses for sensitive info\n"
                "• Add error handling for edge cases\n"
                "• Limit to 5 context menus per bot\n"
                "• Remove commands in cog_unload()\n"
                "• Consider permissions for moderation actions"
            ),
            inline=False,
        )

        embed.add_field(
            name="Limitations",
            value=(
                "• Max 5 user + 5 message context menus per bot\n"
                "• No parameters (unlike slash commands)\n"
                "• Cannot have descriptions\n"
                "• Names must be unique globally"
            ),
            inline=False,
        )

        embed.set_footer(
            text="Try right-clicking a user or message to test the examples!"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="context_test", description="Instructions for testing context menus"
    )
    async def context_test(self, interaction: discord.Interaction):
        """Test message for context menu examples"""
        embed = discord.Embed(
            title="🧪 Context Menu Test",
            description=(
                "This message is perfect for testing context menus!\n\n"
                "**Try this:**\n"
                "1. Right-click (or long-press on mobile) this message\n"
                "2. Select 'Apps' from the menu\n"
                "3. Try these context menu commands:\n"
                "   • Quote Message\n"
                "   • Analyze Message\n"
                "   • Translate\n\n"
                "**For user context menus:**\n"
                "1. Right-click any user (including yourself)\n"
                "2. Select 'Apps'\n"
                "3. Try:\n"
                "   • User Info\n"
                "   • Get Avatar"
            ),
            color=MAIN_EMBED_COLOR,
        )

        embed.add_field(
            name="📱 Mobile Users",
            value="Long-press the message or user, then tap 'Apps'",
            inline=False,
        )

        embed.set_footer(
            text="Context menus are quick actions that don't require typing!"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: "RickBot"):
    """Load the ContextMenuExamples cog"""
    await bot.add_cog(ContextMenuExamples(bot))
