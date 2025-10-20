"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - UI Showcase Cog

Demonstrates modern discord.py UI components (buttons, selects, modals, persistent views).
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING, List

from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR, SUCCESS_EMBED_COLOR

if TYPE_CHECKING:
    from core.bot import RickBot


# ===========================
# Button Examples
# ===========================


class BasicButtonsView(discord.ui.View):
    """Demonstrate different button styles"""

    def __init__(self):
        super().__init__(timeout=180.0)
        self.clicks = 0
        # Add link button directly (can't use decorator for links)
        self.add_item(
            discord.ui.Button(
                label="Link",
                style=discord.ButtonStyle.link,
                url="https://discord.py.readthedocs.io/",
            )
        )

    @discord.ui.button(label="Primary", style=discord.ButtonStyle.primary)
    async def primary_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.clicks += 1
        await interaction.response.send_message(
            f"✅ Primary button clicked! (Total clicks: {self.clicks})", ephemeral=True
        )

    @discord.ui.button(label="Secondary", style=discord.ButtonStyle.secondary)
    async def secondary_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "⚪ Secondary button clicked!", ephemeral=True
        )

    @discord.ui.button(label="Success", style=discord.ButtonStyle.success)
    async def success_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "✅ Success button clicked!", ephemeral=True
        )

    @discord.ui.button(label="Danger", style=discord.ButtonStyle.danger)
    async def danger_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "⚠️ Danger button clicked!", ephemeral=True
        )


class DynamicButtonsView(discord.ui.View):
    """Buttons that change state dynamically"""

    def __init__(self):
        super().__init__(timeout=180.0)
        self.enabled = True
        self.counter = 0

    @discord.ui.button(label="Toggle State", style=discord.ButtonStyle.primary)
    async def toggle_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.enabled = not self.enabled
        self.counter_button.disabled = not self.enabled

        if self.enabled:
            button.style = discord.ButtonStyle.success
            button.label = "Enabled ✅"
        else:
            button.style = discord.ButtonStyle.danger
            button.label = "Disabled ❌"

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Counter: 0", style=discord.ButtonStyle.secondary)
    async def counter_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.counter += 1
        button.label = f"Counter: {self.counter}"
        await interaction.response.edit_message(view=self)


# ===========================
# Select Menu Examples
# ===========================


class SelectMenusView(discord.ui.View):
    """Demonstrate different select menu types"""

    def __init__(self):
        super().__init__(timeout=180.0)

    @discord.ui.select(
        placeholder="Choose your favorite color...",
        options=[
            discord.SelectOption(
                label="Red", description="The color of passion", emoji="🔴"
            ),
            discord.SelectOption(
                label="Blue", description="The color of calm", emoji="🔵"
            ),
            discord.SelectOption(
                label="Green", description="The color of nature", emoji="🟢"
            ),
            discord.SelectOption(
                label="Yellow", description="The color of sunshine", emoji="🟡"
            ),
            discord.SelectOption(
                label="Purple", description="The color of royalty", emoji="🟣"
            ),
        ],
    )
    async def color_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        selected = select.values[0]
        await interaction.response.send_message(
            f"You selected: **{selected}**", ephemeral=True
        )

    @discord.ui.select(
        placeholder="Choose multiple options...",
        min_values=1,
        max_values=3,
        options=[
            discord.SelectOption(label="Option 1", emoji="1️⃣"),
            discord.SelectOption(label="Option 2", emoji="2️⃣"),
            discord.SelectOption(label="Option 3", emoji="3️⃣"),
            discord.SelectOption(label="Option 4", emoji="4️⃣"),
            discord.SelectOption(label="Option 5", emoji="5️⃣"),
        ],
    )
    async def multi_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        selected = ", ".join(select.values)
        await interaction.response.send_message(
            f"You selected {len(select.values)} options: **{selected}**", ephemeral=True
        )


class RoleSelectView(discord.ui.View):
    """Demonstrate role select menu"""

    def __init__(self):
        super().__init__(timeout=180.0)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Select roles...",
        min_values=1,
        max_values=5,
    )
    async def role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        roles = ", ".join([role.mention for role in select.values])
        await interaction.response.send_message(
            f"You selected: {roles}", ephemeral=True
        )


class ChannelSelectView(discord.ui.View):
    """Demonstrate channel select menu"""

    def __init__(self):
        super().__init__(timeout=180.0)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Select a channel...",
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.voice,
            discord.ChannelType.forum,
        ],
    )
    async def channel_select(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        channel = select.values[0]
        await interaction.response.send_message(
            f"You selected: {channel.mention} (Type: {channel.type})", ephemeral=True
        )


class UserSelectView(discord.ui.View):
    """Demonstrate user select menu"""

    def __init__(self):
        super().__init__(timeout=180.0)

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Select users...",
        min_values=1,
        max_values=5,
    )
    async def user_select(
        self, interaction: discord.Interaction, select: discord.ui.UserSelect
    ):
        users = ", ".join([user.mention for user in select.values])
        await interaction.response.send_message(
            f"You selected: {users}", ephemeral=True
        )


# ===========================
# Modal Examples
# ===========================


class FeedbackModal(discord.ui.Modal, title="Submit Feedback"):
    """Simple feedback form modal"""

    feedback_type = discord.ui.TextInput(
        label="Feedback Type",
        placeholder="Bug Report, Feature Request, etc.",
        style=discord.TextStyle.short,
        required=True,
        max_length=50,
    )

    feedback_text = discord.ui.TextInput(
        label="Your Feedback",
        placeholder="Tell us what you think...",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=10,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Feedback Submitted",
            description="Thank you for your feedback!",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.add_field(name="Type", value=self.feedback_type.value, inline=False)
        embed.add_field(name="Feedback", value=self.feedback_text.value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class ProfileModal(discord.ui.Modal, title="Edit Profile"):
    """Multi-field profile editing modal"""

    display_name = discord.ui.TextInput(
        label="Display Name",
        placeholder="Your display name...",
        style=discord.TextStyle.short,
        required=True,
        max_length=32,
    )

    bio = discord.ui.TextInput(
        label="Bio",
        placeholder="Tell us about yourself...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=200,
    )

    favorite_game = discord.ui.TextInput(
        label="Favorite Game",
        placeholder="What's your favorite game?",
        style=discord.TextStyle.short,
        required=False,
        max_length=50,
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="✅ Profile Updated", color=SUCCESS_EMBED_COLOR)
        embed.add_field(
            name="Display Name", value=self.display_name.value, inline=False
        )
        if self.bio.value:
            embed.add_field(name="Bio", value=self.bio.value, inline=False)
        if self.favorite_game.value:
            embed.add_field(
                name="Favorite Game", value=self.favorite_game.value, inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class ModalButtonView(discord.ui.View):
    """Button that opens a modal"""

    def __init__(self):
        super().__init__(timeout=180.0)

    @discord.ui.button(label="📝 Submit Feedback", style=discord.ButtonStyle.primary)
    async def feedback_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(FeedbackModal())

    @discord.ui.button(label="👤 Edit Profile", style=discord.ButtonStyle.secondary)
    async def profile_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(ProfileModal())


# ===========================
# Persistent View Example
# ===========================


class PersistentView(discord.ui.View):
    """
    Persistent view that survives bot restarts.

    IMPORTANT: Must be added to bot with bot.add_view() on startup!
    """

    def __init__(self):
        super().__init__(timeout=None)  # No timeout for persistent views

    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.success,
        custom_id="persistent_verify_button",  # MUST have custom_id for persistence
    )
    async def verify_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="✅ Verified",
            description="You've been verified! This button persists across bot restarts.",
            color=SUCCESS_EMBED_COLOR,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Get Role",
        style=discord.ButtonStyle.primary,
        custom_id="persistent_role_button",
    )
    async def role_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🎭 Role system would be implemented here!", ephemeral=True
        )


# ===========================
# Complex Combined Example
# ===========================


class ComplexInteractionView(discord.ui.View):
    """Demonstrates multiple UI components working together"""

    def __init__(self):
        super().__init__(timeout=300.0)
        self.selections = {"color": None, "action": None}

    @discord.ui.select(
        placeholder="Step 1: Choose a color...",
        options=[
            discord.SelectOption(label="Red", emoji="🔴"),
            discord.SelectOption(label="Blue", emoji="🔵"),
            discord.SelectOption(label="Green", emoji="🟢"),
        ],
    )
    async def color_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        self.selections["color"] = select.values[0]
        await interaction.response.send_message(
            f"✅ Selected color: **{select.values[0]}**", ephemeral=True
        )
        self._update_confirm_button()

    @discord.ui.select(
        placeholder="Step 2: Choose an action...",
        options=[
            discord.SelectOption(label="Create", emoji="➕"),
            discord.SelectOption(label="Update", emoji="🔄"),
            discord.SelectOption(label="Delete", emoji="🗑️"),
        ],
    )
    async def action_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        self.selections["action"] = select.values[0]
        await interaction.response.send_message(
            f"✅ Selected action: **{select.values[0]}**", ephemeral=True
        )
        self._update_confirm_button()

    @discord.ui.button(
        label="Confirm", style=discord.ButtonStyle.success, disabled=True, row=2
    )
    async def confirm_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="✅ Confirmed",
            description="Your selections have been confirmed!",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.add_field(name="Color", value=self.selections["color"], inline=True)
        embed.add_field(name="Action", value=self.selections["action"], inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Reset", style=discord.ButtonStyle.danger, row=2)
    async def reset_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.selections = {"color": None, "action": None}
        self.confirm_button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("🔄 Reset complete!", ephemeral=True)

    def _update_confirm_button(self):
        """Enable confirm button when all selections are made"""
        self.confirm_button.disabled = not all(self.selections.values())


# ===========================
# Cog Definition
# ===========================


class UIShowcase(commands.Cog):
    """Interactive UI component examples and demonstrations"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

        # Register persistent views on cog load
        self.bot.add_view(PersistentView())

    @app_commands.command(
        name="ui_buttons", description="Demonstrate button components"
    )
    async def ui_buttons(self, interaction: discord.Interaction):
        """Show basic button examples"""
        embed = discord.Embed(
            title="🔘 Button Examples",
            description="Try out different button styles and interactions!",
            color=MAIN_EMBED_COLOR,
        )
        embed.add_field(
            name="Button Styles",
            value="Primary, Secondary, Success, Danger, Link",
            inline=False,
        )

        view = BasicButtonsView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="ui_dynamic", description="Demonstrate dynamic button states"
    )
    async def ui_dynamic(self, interaction: discord.Interaction):
        """Show buttons that change dynamically"""
        embed = discord.Embed(
            title="⚡ Dynamic Buttons",
            description="Buttons can change their state, label, and style!",
            color=MAIN_EMBED_COLOR,
        )

        view = DynamicButtonsView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="ui_select", description="Demonstrate select menus")
    async def ui_select(self, interaction: discord.Interaction):
        """Show string select menu examples"""
        embed = discord.Embed(
            title="📋 Select Menu Examples",
            description="Select menus allow users to choose from dropdown options!",
            color=MAIN_EMBED_COLOR,
        )

        view = SelectMenusView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="ui_role_select", description="Demonstrate role select menu"
    )
    @app_commands.guild_only()
    async def ui_role_select(self, interaction: discord.Interaction):
        """Show role select menu"""
        embed = discord.Embed(
            title="🎭 Role Select",
            description="Role select menus let users choose roles!",
            color=MAIN_EMBED_COLOR,
        )

        view = RoleSelectView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(
        name="ui_channel_select", description="Demonstrate channel select menu"
    )
    @app_commands.guild_only()
    async def ui_channel_select(self, interaction: discord.Interaction):
        """Show channel select menu"""
        embed = discord.Embed(
            title="📺 Channel Select",
            description="Channel select menus let users choose channels!",
            color=MAIN_EMBED_COLOR,
        )

        view = ChannelSelectView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(
        name="ui_user_select", description="Demonstrate user select menu"
    )
    @app_commands.guild_only()
    async def ui_user_select(self, interaction: discord.Interaction):
        """Show user select menu"""
        embed = discord.Embed(
            title="👥 User Select",
            description="User select menus let users choose members!",
            color=MAIN_EMBED_COLOR,
        )

        view = UserSelectView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="ui_modal", description="Demonstrate modals (forms)")
    async def ui_modal(self, interaction: discord.Interaction):
        """Show modal examples"""
        embed = discord.Embed(
            title="📝 Modal Examples",
            description="Click a button to open a modal form!",
            color=MAIN_EMBED_COLOR,
        )
        embed.add_field(
            name="What are Modals?",
            value="Modals are pop-up forms that collect text input from users.",
            inline=False,
        )

        view = ModalButtonView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="ui_persistent", description="Demonstrate persistent views"
    )
    async def ui_persistent(self, interaction: discord.Interaction):
        """Show persistent view example"""
        embed = discord.Embed(
            title="♾️ Persistent View",
            description=(
                "These buttons persist across bot restarts!\n\n"
                "**How it works:**\n"
                "- Views with `timeout=None`\n"
                "- Buttons have `custom_id` set\n"
                "- View registered with `bot.add_view()` on startup"
            ),
            color=MAIN_EMBED_COLOR,
        )

        view = PersistentView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="ui_complex", description="Demonstrate complex combined interactions"
    )
    async def ui_complex(self, interaction: discord.Interaction):
        """Show complex interaction example"""
        embed = discord.Embed(
            title="🎯 Complex Interaction Example",
            description=(
                "This demonstrates multiple UI components working together!\n\n"
                "**Steps:**\n"
                "1. Choose a color from the first dropdown\n"
                "2. Choose an action from the second dropdown\n"
                "3. Click 'Confirm' when ready (or 'Reset' to start over)"
            ),
            color=MAIN_EMBED_COLOR,
        )

        view = ComplexInteractionView()
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: "RickBot"):
    """Load the UIShowcase cog"""
    await bot.add_cog(UIShowcase(bot))
