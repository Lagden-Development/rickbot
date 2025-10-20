"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

Custom colored logging utilities for RickBot.

Provides beautiful console output with colors, boxes, progress bars, and more.

Who ever said a console has to be boring?
"""

import logging
import platform
import sys
import time
import re
from typing import Optional
from termcolor import colored


def _strip_ansi(text: str) -> str:
    """
    Strip ANSI color codes from text.

    Args:
        text: Text potentially containing ANSI codes

    Returns:
        Text with ANSI codes removed
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def _visible_length(text: str) -> int:
    """
    Get the visible length of text (excluding ANSI codes).

    Args:
        text: Text potentially containing ANSI codes

    Returns:
        Visible character count
    """
    return len(_strip_ansi(text))


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels"""

    # Color mapping for log levels
    LEVEL_COLORS = {
        "DEBUG": ("cyan", []),
        "INFO": ("green", []),
        "WARNING": ("yellow", []),
        "ERROR": ("red", []),
        "CRITICAL": ("red", ["bold"]),
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        # Get color for this level
        color, attrs = self.LEVEL_COLORS.get(record.levelname, ("white", []))

        # Color the level name
        record.levelname = colored(record.levelname, color, attrs=attrs)

        # Format the message using parent formatter
        return super().format(record)


class ProgressBar:
    """Simple progress bar renderer"""

    def __init__(self, total: int, width: int = 30, prefix: str = ""):
        self.total = total
        self.current = 0
        self.width = width
        self.prefix = prefix
        self.start_time = time.time()

    def update(self, current: int) -> None:
        """Update and print progress bar"""
        self.current = current
        self._render()

    def increment(self) -> None:
        """Increment progress by 1"""
        self.current += 1
        self._render()

    def _render(self) -> None:
        """Render the progress bar"""
        if self.total == 0:
            percent = 100
        else:
            percent = (self.current / self.total) * 100

        filled = (
            int(self.width * self.current // self.total)
            if self.total > 0
            else self.width
        )
        bar = "=" * filled + ">" if filled < self.width else "=" * self.width
        bar = bar.ljust(self.width)

        # Calculate elapsed time
        elapsed = time.time() - self.start_time

        # Color the bar based on progress
        if self.current >= self.total:
            bar_colored = colored(f"[{bar}]", "green", attrs=["bold"])
        else:
            bar_colored = colored(f"[{bar}]", "cyan")

        # Print with carriage return to overwrite
        count_str = colored(f"{self.current}/{self.total}", "white", attrs=["bold"])
        percent_str = colored(f"{percent:>3.0f}%", "yellow")
        time_str = colored(f"{elapsed:.1f}s", "cyan")

        output = (
            f"\r  {self.prefix}{bar_colored} {count_str} {percent_str} ({time_str})"
        )
        print(output, end="", flush=True)

        # New line when complete
        if self.current >= self.total:
            print()


def print_box(title: str, content: list[str], color: str = "cyan") -> None:
    """
    Print a fancy box with title and content.

    Args:
        title: Box title
        content: List of content lines
        color: Box color (default: cyan)
    """
    # Calculate box width based on visible content (excluding ANSI codes)
    max_width = (
        max(_visible_length(line) for line in content + [title])
        if content
        else _visible_length(title)
    )
    box_width = max(max_width + 4, 50)  # At least 50 chars wide

    # Top border
    print(colored("╔" + "═" * (box_width - 2) + "╗", color))

    # Title
    title_visible_len = _visible_length(title)
    title_padding = (box_width - title_visible_len - 4) // 2
    remaining_padding = box_width - title_visible_len - title_padding - 4
    title_line = "║ " + " " * title_padding + title + " " * remaining_padding + " ║"
    print(colored(title_line, color, attrs=["bold"]))

    # Separator
    print(colored("╠" + "═" * (box_width - 2) + "╣", color))

    # Content
    for line in content:
        line_visible_len = _visible_length(line)
        content_padding = box_width - line_visible_len - 5
        print(
            colored("║  ", color) + line + colored(" " * content_padding + " ║", color)
        )

    # Bottom border
    print(colored("╚" + "═" * (box_width - 2) + "╝", color))


def print_separator(char: str = "─", length: int = 50, color: str = "cyan") -> None:
    """
    Print a colored separator line.

    Args:
        char: Character to use for separator
        length: Length of separator
        color: Color of separator
    """
    print(colored(char * length, color))


def print_checkmark(
    text: str, success: bool = True, duration: Optional[float] = None
) -> None:
    """
    Print a line with a colored checkmark or X.

    Args:
        text: Text to display
        success: If True, show green checkmark; if False, show red X
        duration: Optional duration to display in seconds
    """
    if success:
        symbol = colored("✓", "green", attrs=["bold"])
    else:
        symbol = colored("✗", "red", attrs=["bold"])

    output = f"  {symbol} {text}"

    if duration is not None:
        duration_str = colored(f"({duration:.2f}s)", "cyan")
        output += f" {duration_str}"

    print(output)


def format_duration(seconds: float) -> str:
    """
    Format duration in a human-readable way.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1.23s", "2m 15s")
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"


def get_system_info() -> dict:
    """
    Get system information for display.

    Returns:
        Dictionary with system info
    """
    return {
        "python_version": f"Python {sys.version.split()[0]}",
        "platform": f"{platform.system()} {platform.machine()}",
        "platform_version": platform.version(),
    }


def print_startup_banner(bot_name: str = "RickBot") -> None:
    """
    Print a startup banner with system information.

    Args:
        bot_name: Name of the bot
    """
    info = get_system_info()

    content = [
        colored("Starting up...", "white", attrs=["bold"]),
        "",
        f"{colored('Platform:', 'yellow')} {info['platform']}",
        f"{colored('Python:', 'yellow')} {info['python_version']}",
    ]

    # Add discord.py version if available
    try:
        import discord

        content.append(f"{colored('Discord.py:', 'yellow')} {discord.__version__}")
    except ImportError:
        pass

    print()  # Empty line before banner
    print_box(f"{bot_name} Starting", content, color="magenta")
    print()  # Empty line after banner


def print_phase_start(phase_name: str) -> None:
    """
    Print a phase start message.

    Args:
        phase_name: Name of the phase starting
    """
    icon = colored("▶", "cyan", attrs=["bold"])
    text = colored(phase_name, "white", attrs=["bold"])
    print(f"\n{icon} {text}")


def print_phase_complete(phase_name: str, duration: float) -> None:
    """
    Print a phase completion message.

    Args:
        phase_name: Name of the phase that completed
        duration: Duration in seconds
    """
    print_checkmark(f"{phase_name} complete", success=True, duration=duration)


def create_logger_with_color(name: str) -> logging.Logger:
    """
    Create a logger with colored formatting.

    Args:
        name: Logger name

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create colored handler
    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "[{asctime}] [{levelname}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
