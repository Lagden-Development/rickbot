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
loop = asyncio.get_event_loop()

for s in [signal.SIGTERM, signal.SIGINT]:
    loop.add_signal_handler(s, lambda s=s: asyncio.create_task(bot.shutdown(s)))

loop.run_until_complete(bot.start_bot())
