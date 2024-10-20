"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This script is responsible for running the bot. It sets up the necessary environment, handles signals for
graceful shutdowns, and initiates the bot's main loop. The bot's core functionality is encapsulated in the
RickBot class, which is imported and used here.
"""

import os
import configparser
import getpass
import asyncio
import signal
from typing import NoReturn
from dotenv import load_dotenv
from contextlib import suppress

from helpers.logs import RICKLOG_MAIN
from rickbot.main import RickBot

# Adjust the current working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_valid_input(
    prompt: str,
    input_type: str = "input",
    error_message: str = "Invalid input. Please try again.",
) -> str:
    """
    Get valid input from the user.

    Args:
        prompt (str): The prompt to display to the user.
        input_type (str): The type of input to get ("input" or "getpass").
        error_message (str): The error message to display if input is invalid.

    Returns:
        str: The valid input from the user.
    """
    while True:
        if input_type == "getpass":
            user_input = getpass.getpass(prompt)
        else:
            user_input = input(prompt)
        if user_input:
            return user_input
        RICKLOG_MAIN.error(error_message)


def initial_setup_process() -> None:
    """
    The initial setup process for the bot.
    """
    RICKLOG_MAIN.info(
        "It looks like this is your first time running RickBot, so we'll need to do some initial setup..."
    )

    token = get_valid_input(
        "Enter your bot's token: ", "getpass", "Invalid token. Please try again."
    )
    mongo_uri = get_valid_input(
        "Enter your MongoDB URI: ", "getpass", "Invalid MongoDB URI. Please try again."
    )
    prefix = get_valid_input("Enter your bot's prefix: ")
    dev_id = get_valid_input("Enter your Discord ID: ")

    # Create the .env file
    with open(".env", "w") as f:
        f.write(f"TOKEN={token}\n")
        f.write(f"MONGO_URI={mongo_uri}\n")

    # Update the config.ini file
    config = configparser.ConfigParser()
    config.read("config.ini")
    config["MAIN"]["dev"] = dev_id
    config["BOT"]["prefix"] = prefix
    with open("config.ini", "w") as f:
        config.write(f)

    RICKLOG_MAIN.info(
        "Initial setup complete. You can further configure the bot by editing the config.ini file."
    )
    RICKLOG_MAIN.info(
        "To use a different configuration, delete the .env file and run the script again."
    )
    RICKLOG_MAIN.info(
        "For help, please visit: https://github.com/Lagden-Development/rickbot"
    )


# Initialize the bot
bot = RickBot()


async def main() -> NoReturn:
    """
    The main function responsible for starting and managing the bot.

    This function sets up signal handlers for graceful shutdowns and then starts the bot.
    It handles SIGTERM and SIGINT signals for proper termination.

    Returns:
        NoReturn: This function runs indefinitely until interrupted.

    Raises:
        Exception: Any unhandled exceptions during bot operation are logged.
    """
    loop = asyncio.get_running_loop()

    def signal_handler(sig: signal.Signals) -> None:
        """
        Handle incoming signals for bot shutdown.

        Args:
            sig (signal.Signals): The signal received (SIGTERM or SIGINT).
        """
        RICKLOG_MAIN.info(f"Received signal {sig.name}. Initiating shutdown...")
        asyncio.create_task(bot.shutdown(sig.name))

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))

    try:
        await bot.start_bot()
    except Exception as e:
        RICKLOG_MAIN.error(f"Unhandled exception in main loop: {e}", exc_info=True)
    finally:
        RICKLOG_MAIN.info("Rickbot is shutting down...")
        await bot.close()


if __name__ == "__main__":
    """
    Entry point of the script.

    Runs the main coroutine and handles graceful shutdown on interruption.
    """
    if not os.path.exists(".env"):
        initial_setup_process()

    load_dotenv()

    with suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
    RICKLOG_MAIN.info("Rickbot has shut down successfully.")
