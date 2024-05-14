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
RICKLOG.setLevel(logging.INFO)

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
