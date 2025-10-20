"""
(c) 2025 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

RickBot 2.0 - Application Entry Point

Production-grade Discord bot with graceful shutdown and structured logging.
"""

import asyncio
import signal
import sys
import warnings
from pathlib import Path
import logging
import time
from dotenv import load_dotenv

from core import RickBot, Config
from helpers.logger import (
    ColoredFormatter,
    print_startup_banner,
    print_box,
    format_duration,
    print_checkmark,
)
from helpers.rickbot import get_goodbye_message

# Configure colored logging
handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "[{asctime}] [{levelname}] {name}: {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
handler.setFormatter(formatter)

# Configure root logger
logging.root.handlers.clear()
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

# Suppress asyncio ResourceWarnings (harmless Discord.py cleanup warnings)
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")

logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Main application entry point.

    Handles:
    - Configuration loading
    - Bot initialization
    - Graceful shutdown on signals
    """
    # Track total startup time
    startup_start = time.time()

    # Print startup banner
    print_startup_banner("RickBot 2.0")

    # Change to script directory
    script_dir = Path(__file__).parent
    import os

    os.chdir(script_dir)

    # Load environment variables
    load_dotenv()
    print_checkmark("Environment variables loaded", success=True)

    # Check if config exists, create template if not
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.warning("Config file not found, creating template...")
        Config.save_template(config_path)
        logger.error(
            "Configuration template created at config.yaml\n"
            "Please edit this file and set your environment variables before starting the bot."
        )
        sys.exit(1)

    # Load configuration
    try:
        config = Config.load(config_path)
        print_checkmark("Configuration loaded successfully", success=True)
    except Exception as e:
        print_checkmark(f"Failed to load configuration: {e}", success=False)
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        sys.exit(1)

    # Configure logging level from config
    logging.getLogger().setLevel(logging.getLevelName(config.logging.level))

    if config.logging.log_discord_library:
        logging.getLogger("discord").setLevel(logging.DEBUG)
    else:
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("discord.http").setLevel(logging.WARNING)

    # Initialize bot
    bot = RickBot(config)

    # Setup graceful shutdown
    loop = asyncio.get_running_loop()

    def signal_handler(sig: signal.Signals) -> None:
        """Handle shutdown signals"""
        logger.info(f"Received signal {sig.name}, shutting down gracefully...")
        asyncio.create_task(bot.close())

    # Register signal handlers (Unix only)
    if sys.platform != "win32":
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
    else:
        # Windows doesn't support add_signal_handler
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(signal.SIGINT))

    # Run bot
    try:
        print()  # Empty line before starting
        logger.debug("Starting RickBot...")
        await bot.start(config.bot.token)
    except KeyboardInterrupt:
        print()  # Empty line before shutdown message
        logger.info("Keyboard interrupt received")
    except Exception as e:
        print()  # Empty line before error
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if not bot.is_closed():
            await bot.close()

        # Calculate total runtime
        total_runtime = time.time() - startup_start

        # Print shutdown box
        print()
        shutdown_content = [
            f"Total runtime: {format_duration(total_runtime)}",
            "All systems shut down gracefully",
            "",
            get_goodbye_message(),
        ]
        print_box("RickBot Shutdown Complete", shutdown_content, color="magenta")
        print()


if __name__ == "__main__":
    """Entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Handled in main()
