"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Reusable UI Components

Common View classes for buttons, pagination, confirmations, etc.
"""

import discord
from discord import ui
from typing import List, Callable, Optional, Any
from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR, SUCCESS_EMBED_COLOR


class PaginatedView(ui.View):
    """Reusable pagination view for embeds"""

    def __init__(
        self,
        embeds: List[discord.Embed],
        *,
        timeout: float = 180.0,
        author_id: Optional[int] = None,
    ):
        """
        Initialize paginated view.

        Args:
            embeds: List of embeds to paginate through
            timeout: View timeout in seconds
            author_id: User ID who can use the buttons (None = anyone)
        """
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.author_id = author_id

        # Update button states
        self._update_buttons()

    def _update_buttons(self) -> None:
        """Update button states based on current page"""
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.embeds) - 1
        self.last_page.disabled = self.current_page == len(self.embeds) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if user can interact with buttons"""
        if self.author_id and interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot use these buttons!", ephemeral=True
            )
            return False
        return True

    @ui.button(label="⏮️", style=discord.ButtonStyle.gray, disabled=True)
    async def first_page(self, interaction: discord.Interaction, button: ui.Button):
        """Go to first page"""
        self.current_page = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[0], view=self)

    @ui.button(label="◀️", style=discord.ButtonStyle.gray, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: ui.Button):
        """Go to previous page"""
        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @ui.button(label="▶️", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        """Go to next page"""
        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @ui.button(label="⏭️", style=discord.ButtonStyle.gray)
    async def last_page(self, interaction: discord.Interaction, button: ui.Button):
        """Go to last page"""
        self.current_page = len(self.embeds) - 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )


class ConfirmationView(ui.View):
    """Reusable confirmation dialog"""

    def __init__(
        self,
        *,
        timeout: float = 60.0,
        author_id: int,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
    ):
        """
        Initialize confirmation view.

        Args:
            timeout: View timeout in seconds
            author_id: User ID who can confirm
            confirm_label: Label for confirm button
            cancel_label: Label for cancel button
        """
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.value: Optional[bool] = None

        # Update button labels
        self.confirm_button.label = confirm_label
        self.cancel_button.label = cancel_label

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the author to interact"""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot use these buttons!", ephemeral=True
            )
            return False
        return True

    @ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        """Confirm action"""
        self.value = True
        self.stop()
        await interaction.response.edit_message(view=None)

    @ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):
        """Cancel action"""
        self.value = False
        self.stop()
        await interaction.response.edit_message(view=None)


class ErrorViewer(ui.View):
    """View for browsing database errors"""

    def __init__(self, errors: List[Any], db: Any):
        """
        Initialize error viewer.

        Args:
            errors: List of ErrorLog objects
            db: Database instance
        """
        super().__init__(timeout=300.0)
        self.errors = errors
        self.db = db
        self.current_index = 0

        if not errors:
            # Disable buttons if no errors
            for item in self.children:
                item.disabled = True

    @ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray)
    async def previous_error(self, interaction: discord.Interaction, button: ui.Button):
        """Show previous error"""
        if self.current_index > 0:
            self.current_index -= 1
            embed = self._build_error_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Already at first error!", ephemeral=True
            )

    @ui.button(label="Next ▶️", style=discord.ButtonStyle.gray)
    async def next_error(self, interaction: discord.Interaction, button: ui.Button):
        """Show next error"""
        if self.current_index < len(self.errors) - 1:
            self.current_index += 1
            embed = self._build_error_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Already at last error!", ephemeral=True
            )

    @ui.button(label="✅ Mark Resolved", style=discord.ButtonStyle.success)
    async def mark_resolved(self, interaction: discord.Interaction, button: ui.Button):
        """Mark error as resolved"""
        error = self.errors[self.current_index]

        # Update in database
        await self.db.error_logs.update_one(
            {"error_reference": error.error_reference}, {"resolved": True}
        )

        await interaction.response.send_message(
            f"✅ Marked error {error.error_reference} as resolved!", ephemeral=True
        )

    def _build_error_embed(self) -> discord.Embed:
        """Build embed for current error"""
        if not self.errors:
            return discord.Embed(
                title="No Errors Found",
                description="No errors in the database!",
                color=SUCCESS_EMBED_COLOR,
            )

        error = self.errors[self.current_index]
        embed = discord.Embed(
            title=f"Error {error.error_reference}",
            description=f"**Type:** `{error.error_type}`\n**Message:** {error.error_message}",
            color=ERROR_EMBED_COLOR,
            timestamp=error.occurred_at,
        )

        if error.command_name:
            embed.add_field(name="Command", value=error.command_name, inline=True)
        if error.guild_id:
            embed.add_field(name="Guild ID", value=str(error.guild_id), inline=True)
        if error.user_id:
            embed.add_field(name="User ID", value=str(error.user_id), inline=True)

        if error.traceback:
            # Truncate traceback to fit in embed
            tb = (
                error.traceback[:1000] + "..."
                if len(error.traceback) > 1000
                else error.traceback
            )
            embed.add_field(
                name="Traceback", value=f"```python\n{tb}\n```", inline=False
            )

        embed.set_footer(text=f"Error {self.current_index + 1} of {len(self.errors)}")

        if error.resolved:
            embed.color = SUCCESS_EMBED_COLOR
            embed.title += " (Resolved)"

        return embed
