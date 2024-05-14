"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the config file for RickBot.
"""

CONFIG = {
    "mode": "dev",  # "dev" or "prod"
    "bot": {
        "token": "bot token",
        "prefix": ".",
        "status": {
            "type": "playing",
            "message": "a game!",
        },
    },
    "behaviour": {
        "continue_to_load_cogs_after_failure": False,
        # "afk_timeout": 300,
    },
    "mongo": {
        "uri": "uri",
        "bot_specific_db": "bot",
    },
}
