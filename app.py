"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This script is responsible for running the bot. It sets up the necessary environment, handles signals for
graceful shutdowns, and initiates the bot's main loop. The bot's core functionality is encapsulated in the
RickBot class, which is imported and used here.
"""

# Import the required modules

# Python Standard Library
# -----------------------
from typing import (
    NoReturn,
)  # The build in typing module, used for type hints and annotations.
import asyncio  # For handling asynchronous operations, which are crucial for the bot's functionality.
import signal  # To handle signals like SIGTERM and SIGINT, allowing for graceful shutdowns.
import os  # Provides a way to interact with the operating system, specifically for handling file paths.

# Internal Modules
# ------------------------
from rickbot.main import (
    RickBot,
)  # Importing the RickBot class, which contains the core logic and behavior of the bot.


# Adjust the current working directory
# ------------------------------------
# This ensures that the script's directory is the working directory, no matter where it's run from.
# It's a safeguard to ensure that all relative paths within the bot's operations are correctly resolved.
abspath = os.path.abspath(__file__)  # Get the absolute path of this file.
dname = os.path.dirname(abspath)  # Determine the directory name of this file.
os.chdir(dname)  # Change the current working directory to this file's directory.

# Initialize the bot
# ------------------
# Create an instance of RickBot, which will be used to run and manage the bot's operations.
# This instance encapsulates all the methods and properties necessary for the bot to function.
bot = RickBot()


async def main() -> NoReturn:
    """
    The main function responsible for starting and managing the bot.

    This function sets up signal handlers for graceful shutdowns and then starts the bot.
    The signal handlers listen for SIGTERM and SIGINT, which are signals for termination
    and interruption (e.g., Ctrl+C), respectively. When such a signal is received, the bot's
    shutdown procedure is initiated.

    Returns:
        NoReturn: This function does not return anything.
    """
    # Set up signal handlers for graceful shutdown
    # --------------------------------------------
    # This loop iterates over the signals SIGTERM and SIGINT, adding a handler for each.
    # The handler triggers the bot's shutdown method, allowing for a clean exit.
    for s in [signal.SIGTERM, signal.SIGINT]:
        asyncio.get_event_loop().add_signal_handler(
            s, lambda s=s: asyncio.create_task(bot.shutdown(s))
        )

    # Start the bot
    # -------------
    # This line initiates the bot's main functionality, entering its event loop until shutdown is triggered.
    await bot.start_bot()


# Entry point for the script
# --------------------------
# This block ensures that the script can be run as a standalone program.
# It tries to run the main asynchronous function, handling common exit scenarios gracefully.
if __name__ == "__main__":
    try:
        # Run the main asynchronous function
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Handle common exit scenarios like keyboard interruption (Ctrl+C) or system exit.
        print("Bot shutdown requested, exiting...")
    except Exception as e:
        # Catch any other exceptions that might occur and log them.
        print(f"Unhandled exception: {e}")
