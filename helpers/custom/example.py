"""
Example custom helper module.

Add your own helper functions, classes, and utilities here.
Delete this file once you've added your own.
"""

import discord
from typing import Optional


async def example_helper_function(
    interaction: discord.Interaction, message: str
) -> None:
    """
    Example helper function.

    Args:
        interaction: Discord interaction
        message: Message to send
    """
    await interaction.response.send_message(message, ephemeral=True)


class ExampleUtility:
    """Example utility class"""

    def __init__(self, bot):
        self.bot = bot

    async def do_something(self) -> Optional[str]:
        """Example method"""
        return f"Bot has {len(self.bot.guilds)} guilds"
