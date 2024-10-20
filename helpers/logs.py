"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This script provides a custom logging setup for RickBot, including formatters with
ANSI color support for console output, and a cleaner formatter for log files.
"""

# Import the required modules

# Python Standard Library
# -----------------------
import logging  # Handles the logging operations, allowing the output of messages to different destinations.
import re  # Provides regular expression matching operations for strings.


# Helper functions
def remove_ansi_escape_sequences(s: str) -> str:
    """
    Removes ANSI escape sequences from a string. This is useful for cleaning up
    log messages before saving them to a file, ensuring no color codes are stored.

    Args:
        s (str): The string from which to remove ANSI escape sequences.

    Returns:
        str: The cleaned string with no ANSI escape sequences.
    """
    # ANSI escape sequences regex pattern
    ansi_escape_pattern = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    return ansi_escape_pattern.sub("", s)


# Custom formatter class with colors
class CustomFormatter(logging.Formatter):
    """
    A custom logging formatter that adds color to log messages using ANSI escape sequences.
    This is particularly useful for enhancing readability when viewing logs in the console.

    Attributes:
        COLORS (dict): A dictionary mapping log levels to their respective ANSI color codes.
        RESET (str): The ANSI code to reset the color back to the default.
    """

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

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record with colors for different log levels.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message with ANSI color codes.
        """
        log_fmt = (
            f'{self.COLORS.get("DATE")}%(asctime)s{self.RESET} '
            f'{self.COLORS.get(record.levelname, "")}%(levelname)s{self.RESET}     '
            f'{self.COLORS.get("NAME")}%(name)s{self.RESET} %(message)s'
        )
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


# Custom formatter that removes ANSI colors
class CustomFileFormatter(logging.Formatter):
    """
    A custom logging formatter that strips ANSI color codes from log messages.
    This is used for log files to ensure that no unwanted color codes are saved.

    Methods:
        format(record): Strips ANSI codes from the formatted log message.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record by removing any ANSI color codes.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message without ANSI color codes.
        """
        original_format = super().format(record)
        return remove_ansi_escape_sequences(original_format)


# Define the RickBot logger
RICKLOG = logging.getLogger("rickbot")  # The main logger for RickBot.
RICKLOG.setLevel(
    logging.DEBUG
)  # Set the default logging level to DEBUG for comprehensive logging.

# Create a file and console handler
file_handler = logging.FileHandler(
    filename="rickbot.log", mode="w"
)  # File handler to write logs to a file.
console_handler = (
    logging.StreamHandler()
)  # Console handler to output logs to the console.

# Create formatters
file_formatter = CustomFileFormatter(
    "%(asctime)s %(levelname)s     %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)  # Formatter for the file handler, no colors.
console_formatter = CustomFormatter()  # Formatter for the console handler, with colors.

# Set formatters to handlers
file_handler.setFormatter(
    file_formatter
)  # Attach the file formatter to the file handler.
console_handler.setFormatter(
    console_formatter
)  # Attach the console formatter to the console handler.

# Add the handlers to the logger
RICKLOG.addHandler(file_handler)  # Add the file handler to the main RickBot logger.
RICKLOG.addHandler(
    console_handler
)  # Add the console handler to the main RickBot logger.

# Define sub-loggers as constants
RICKLOG_CMDS = logging.getLogger("rickbot.cmds")  # Sub-logger for commands.
RICKLOG_DISCORD = logging.getLogger(
    "rickbot.discord"
)  # Sub-logger for Discord-related logs.
RICKLOG_MAIN = logging.getLogger(
    "rickbot.main"
)  # Sub-logger for main application logs.
RICKLOG_BG = logging.getLogger("rickbot.bg")  # Sub-logger for background task logs.
RICKLOG_HELPERS = logging.getLogger(
    "rickbot.helpers"
)  # Sub-logger for helper function logs.

# Add handlers to sub-loggers
# Currently, this is not required as the handlers are added to the main logger,
# but it's here in case of future needs or changes in how logging is handled.
"""
RICKLOG_CMDS.addHandler(file_handler)
RICKLOG_CMDS.addHandler(console_handler)
RICKLOG_DISCORD.addHandler(file_handler)
RICKLOG_DISCORD.addHandler(console_handler)
RICKLOG_MAIN.addHandler(file_handler)
RICKLOG_MAIN.addHandler(console_handler)
RICKLOG_BG.addHandler(file_handler)
RICKLOG_BG.addHandler(console_handler)
RICKLOG_HELPERS.addHandler(file_handler)
RICKLOG_HELPERS.addHandler(console_handler)
"""


def setup_discord_logging(level: int = logging.INFO) -> None:
    """
    Sets the logging levels for all discord.py related loggers.

    Args:
        level (int): The logging level to set. Must be one of the standard logging levels:
                     DEBUG, INFO, WARNING, ERROR, or CRITICAL.

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


# Example usage of the logging setup
if __name__ == "__main__":
    RICKLOG.info("RickBot logging setup complete.")
    RICKLOG_CMDS.debug("This is a debug message from the cmds sub-logger.")
    RICKLOG_DISCORD.info("This is an info message from the discord sub-logger.")
    RICKLOG_MAIN.warning("This is a warning message from the main sub-logger.")
    RICKLOG_BG.critical("This is a critical message from the background sub-logger.")
    RICKLOG_HELPERS.info("This is an info message from the helpers sub-logger.")
