import os
import configparser

from helpers.logs import RICKLOG_MAIN

CONFIG = configparser.ConfigParser()
CUSTOM_CONFIG = configparser.ConfigParser()

# Ensure the config file exists
if not os.path.exists("config.ini"):
    RICKLOG_MAIN.warning("Config file not found, exiting.")
    exit(1)

# Read the config file
CONFIG.read("config.ini")

# Ensure the custom config file exists
if not os.path.exists("custom_config.ini"):
    RICKLOG_MAIN.warning("Custom config file not found, creating one.")
    with open("custom_config.ini", "w+") as f:
        f.write("[DEFAULT]\n")

# Read the custom config file
CUSTOM_CONFIG.read("custom_config.ini")
