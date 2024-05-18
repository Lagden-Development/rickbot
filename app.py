"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

Runs the bot.
"""

import asyncio
import signal
import os

from rickbot.main import RickBot

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

bot = RickBot()


async def main():
    for s in [signal.SIGTERM, signal.SIGINT]:
        asyncio.get_event_loop().add_signal_handler(
            s, lambda s=s: asyncio.create_task(bot.shutdown(s))
        )

    await bot.start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot shutdown requested, exiting...")
    except Exception as e:
        print(f"Unhandled exception: {e}")
