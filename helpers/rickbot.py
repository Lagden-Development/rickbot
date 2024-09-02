"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This is a helper file full of RickBot specific constants and functions.

Please do not change anything in this file, as it will make me sad,
RickBot is RickBot, and RickBot is perfect. No need to change anything.
"""

# Import the required modules

# Third-party Modules
# -------------------
from termcolor import (
    colored,
)  # Termcolor is used to add color to terminal text, enhancing the readability of console outputs.

# discord.py Library
# ------------------
from discord.ext.commands import (
    Bot,
)  # Importing the Bot class from discord.ext.commands to type hint the bot object.

# Helpers
# -------
from helpers.logs import (
    RICKLOG,
)  # Importing the main logger from the helpers.logs module to log RickBot-specific events.

# Functions
# ---------


def rickbot_start_msg(bot: Bot) -> None:
    """
    Print a message to the console when the bot is ready.

    This function is called when RickBot is fully initialized and ready to start interacting with Discord.
    It prints a stylized message to the console, logging information about the bot, including the number
    of guilds, users, commands, and cogs it has loaded.

    Args:
        bot (Bot): The instance of RickBot that has just started.

    Returns:
        None
    """
    print(
        START_SUCCESS_RICKBOT_ART
    )  # Print the ASCII art for RickBot's startup message.

    # Log the bot's login details with colored output for emphasis.
    RICKLOG.info(f'Logged in as {colored(bot.user.name, "light_cyan", attrs=["bold", "underline"])} with ID {colored(bot.user.id, "light_cyan", attrs=["bold", "underline"])}')  # type: ignore

    # Log extra information about the bot's connections and loaded components.
    RICKLOG.info(
        f'Connected to {colored(len(bot.guilds), "light_cyan", attrs=["bold", "underline"])} guilds.'
    )
    RICKLOG.info(
        f'Connected to {colored(len(bot.users), "light_cyan", attrs=["bold", "underline"])} users.'
    )
    RICKLOG.info(
        f'Loaded {colored(len(bot.commands), "light_cyan", attrs=["bold", "underline"])} commands.'
    )
    RICKLOG.info(
        f'Loaded {colored(len(bot.cogs), "light_cyan", attrs=["bold", "underline"])} cogs.'
    )


# Constants
# ---------

# This constant contains the ASCII art that is printed to the console when RickBot starts.
# The art is a stylized version of RickBot's name, created using text with colored attributes.
START_SUCCESS_RICKBOT_ART = (
    str(
        """
    {0}        {1}
   {2}     {3}
  {4}     {5}
 {6}   {7}
{8} {9}
""".format(
            colored("//   ) )               //", "magenta", attrs=["bold"]),
            colored("//   ) )", "cyan", attrs=["bold"]),
            colored("//___/ /  ( )  ___     //___", "magenta", attrs=["bold"]),
            colored("//___/ /   ___    __  ___", "cyan", attrs=["bold"]),
            colored("/ ___ (   / / //   ) ) //\\ \\", "magenta", attrs=["bold"]),
            colored("/ __  (   //   ) )  / /", "cyan", attrs=["bold"]),
            colored("//   | |  / / //       //  \\ \\", "magenta", attrs=["bold"]),
            colored("//    ) ) //   / /  / /", "cyan", attrs=["bold"]),
            colored("//    | | / / ((____   //    \\ \\", "magenta", attrs=["bold"]),
            colored("//____/ / ((___/ /  / /", "cyan", attrs=["bold"]),
        )
    )
    + "                      "
    + colored("RickBot:", "magenta", attrs=["bold"])
    + " "
    + colored("Ready!", "green", attrs=["bold"])
    + "\n"
)
