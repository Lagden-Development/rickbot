"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the config file for RickBot.
"""

# Import the required modules

# Python standard library
import json
import os

# Helpers
from helpers.logs import RICKLOG_MAIN

# DEFAULT CONFIG

DEFAULT_CONFIG = {
    "mode": "dev",  # "dev" or "prod"
    "devs": [123456789],
    "bot": {
        "token": "BOT TOKEN",
        "prefix": "!",
        "status": {
            "type": "playing",
            "message": "a game",
        },
    },
    "behaviour": {
        "continue_to_load_cogs_after_failure": False,
        # "afk_timeout": 300,
    },
    "mongo": {
        "uri": "mongodb uri",
        "bot_specific_db": "bot",
    },
}

# Custom Config

# Check if the customconfig.json file exists
if os.path.exists("customconfig.json"):
    with open("customconfig.json", "r") as f:
        CUSTOM_CONFIG = json.load(f)
else:
    RICKLOG_MAIN.warning("customconfig.json file not found. Creating a new one.")
    with open("customconfig.json", "w") as f:
        json.dump(
            {"Use this config": "To add custom config data your cogs need."},
            f,
            indent=2,
        )
    CUSTOM_CONFIG = {}


# Main Config

# Check if the config.json file exists
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
else:
    RICKLOG_MAIN.critical(
        "config.json file not found. Bot cannot start. Creating a new one."
    )
    RICKLOG_MAIN.warning("Please fill in the required fields in the config.json file.")
    RICKLOG_MAIN.warning(
        "Once you have filled in the required fields, restart the bot to apply the changes."
    )

    # Create a new config.json file
    with open("config.json", "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    CONFIG = {}

    # Exit the bot
    exit()

"""
Ensure the CONFIG has all the required fields
If the config.json file is missing any required fields, abort the bot and tell the user to fill in the required fields.

We can tell if any fields are missing by ensuring no fields match the default config or are empty.
"""

need_to_exit = False

# Ensure a mode is set
if CONFIG.get("mode") in [None, ""]:
    RICKLOG_MAIN.critical("The 'mode' field in the config.json file is missing.")
    need_to_exit = True

# Ensure the devs list is set
if CONFIG.get("devs") in [None, ""]:
    RICKLOG_MAIN.critical("The 'devs' field in the config.json file is missing.")
    need_to_exit = True

# Ensure the bot settings are set
bot_config = CONFIG.get("bot")

if bot_config.get("token") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'token' field in the bot settings in the config.json file is missing."
    )
    need_to_exit = True

if bot_config.get("prefix") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'prefix' field in the bot settings in the config.json file is missing."
    )
    need_to_exit = True

bot_config_status = bot_config.get("status")

if bot_config_status.get("type") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'type' field in the bot status settings in the config.json file is missing."
    )
    need_to_exit = True

if bot_config_status.get("message") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'message' field in the bot status settings in the config.json file is missing."
    )
    need_to_exit = True

# Ensure the behaviour settings are set
behaviour_config = CONFIG.get("behaviour")

if behaviour_config.get("continue_to_load_cogs_after_failure") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'continue_to_load_cogs_after_failure' field in the behaviour settings in the config.json file is missing."
    )
    need_to_exit = True

# Ensure the mongo settings are set
mongo_config = CONFIG.get("mongo")

if mongo_config.get("uri") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'uri' field in the mongo settings in the config.json file is missing."
    )
    need_to_exit = True

if mongo_config.get("bot_specific_db") in [None, ""]:
    RICKLOG_MAIN.critical(
        "The 'bot_specific_db' field in the mongo settings in the config.json file is missing."
    )
    need_to_exit = True

# Exit the bot if any required fields are missing
if need_to_exit:
    RICKLOG_MAIN.critical(
        "Bot cannot start. Please fill in the required fields in the config.json file."
    )
    RICKLOG_MAIN.warning(
        "Once you have filled in the required fields, restart the bot to apply the changes."
    )
    exit()
