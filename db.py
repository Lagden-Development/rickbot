"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This is the database file for the AR15 website. It contains the database connection logic.
"""

# Import the required modules

# Third Party Modules
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Import configuration
from config import CONFIG

client = MongoClient(CONFIG["mongo"]["uri"], server_api=ServerApi("1"))

bot_db = client["bot"]
messages_collection = bot_db["messages"]
money_collection = bot_db["money"]
invites_collection = bot_db["invites"]


def get_mongo_client():
    return client
