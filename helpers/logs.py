"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is a helper for logging.
"""

# Import the required modules

# Python standard library
import logging
import re

# Helper functions


def remove_ansi_escape_sequences(s: str) -> str:
    # ANSI escape sequences regex pattern
    ansi_escape_pattern = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    return ansi_escape_pattern.sub("", s)


# Custom formatter class with colors
class CustomFormatter(logging.Formatter):
    # ANSI escape sequences for colors
    COLORS = {
        "DEBUG": "\033[1;97m",  # Bold White
        "INFO": "\033[1;94m",  # Bold Blue
        "WARNING": "\033[1;93m",  # Bold Yellow
        "ERROR": "\033[1;91m",  # Bold Red
        "CRITICAL": "\033[1;97;101m",  # Bold Red on White background
        "DATE": "\033[1;30m",  # Bold Grey
        "NAME": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_fmt = f'{self.COLORS.get("DATE")}%(asctime)s{self.RESET} {self.COLORS.get(record.levelname, "")}%(levelname)s{self.RESET}     {self.COLORS.get("NAME")}%(name)s{self.RESET} %(message)s'
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


# Custom formatter that removes ANSI colors
class CustomFileFormatter(logging.Formatter):
    def format(self, record):
        original_format = super().format(record)
        return remove_ansi_escape_sequences(original_format)


# Define the RickBot logger
RICKLOG = logging.getLogger("rickbot")
RICKLOG.setLevel(logging.DEBUG)

# Create a file and console handler
file_handler = logging.FileHandler(filename="rickbot.log", mode="w")
console_handler = logging.StreamHandler()

# Create formatters
file_formatter = CustomFileFormatter(
    "%(asctime)s %(levelname)s     %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_formatter = CustomFormatter()

# Set formatters to handlers
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)

# Add the handlers to the logger
RICKLOG.addHandler(file_handler)
RICKLOG.addHandler(console_handler)

# Define sub-loggers as constants
RICKLOG_CMDS = logging.getLogger("rickbot.cmds")
RICKLOG_DISCORD = logging.getLogger("rickbot.discord")
RICKLOG_MAIN = logging.getLogger("rickbot.main")
RICKLOG_WEBHOOK = logging.getLogger("rickbot.webhook")
RICKLOG_BG = logging.getLogger("rickbot.bg")
RICKLOG_HELPERS = logging.getLogger("rickbot.helpers")

# Add handlers to sub-loggers
# Currently not required as the handlers are added to the main logger
"""
RICKLOG_CMDS.addHandler(file_handler)
RICKLOG_CMDS.addHandler(console_handler)
RICKLOG_DISCORD.addHandler(file_handler)
RICKLOG_DISCORD.addHandler(console_handler)
RICKLOG_MAIN.addHandler(file_handler)
RICKLOG_MAIN.addHandler(console_handler)
RICKLOG_WEBHOOK.addHandler(file_handler)
RICKLOG_WEBHOOK.addHandler(console_handler)
RICKLOG_BG.addHandler(file_handler)
RICKLOG_BG.addHandler(console_handler)
RICKLOG_HELPERS.addHandler(file_handler)
RICKLOG_HELPERS.addHandler(console_handler)
"""


def setup_discord_logging(level=logging.INFO) -> None:
    """
    Sets the levels for all discord.py related loggers.

    Args:
        level (int): The logging level to set.

    Returns:
        None
    """

    if level not in {
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    }:
        raise ValueError("The level must be a valid logging level.")

    # Define discord logging levels
    logging.getLogger("discord.client").setLevel(level)
    logging.getLogger("discord.gateway").setLevel(level)
    logging.getLogger("discord.http").setLevel(level)


# Example usage
if __name__ == "__main__":
    RICKLOG.info("RickBot logging setup complete.")
    RICKLOG_CMDS.debug("This is a debug message from the cmds sub-logger.")
    RICKLOG_DISCORD.info("This is an info message from the discord sub-logger.")
    RICKLOG_MAIN.warning("This is a warning message from the main sub-logger.")
    RICKLOG_WEBHOOK.error("This is an error message from the webhook sub-logger.")
    RICKLOG_BG.critical("This is a critical message from the background sub-logger.")
    RICKLOG_HELPERS.info("This is an info message from the helpers sub-logger.")
