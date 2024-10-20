"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This module handles the database interactions for the bot, specifically focusing on MongoDB operations.
It sets up the connection to the database, provides access to various collections, and offers utility 
functions for obtaining the MongoDB client.
"""

# Standard Modules
# ----------------
import os

# Third Party Modules
# -------------------
from pymongo.mongo_client import (
    MongoClient,
)  # The official MongoDB driver for Python, used to interact with the database.
from pymongo.server_api import (
    ServerApi,
)  # Allows locking the API version to ensure compatibility.

# Internal Modules
# ----------------
from config import CONFIG

# Initialize the MongoDB client
# -----------------------------
# Here we're creating a MongoClient instance using the URI specified in the CONFIG.
# The ServerApi parameter is used to lock the API version to "1", ensuring compatibility and stability.
client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi("1"))

# Database Access
# ------------------------------
# Selecting the database to use with the bot.
# The database name is fetched from the configuration file, allowing easy switching of databases by
# simply modifying the configuration, without needing to alter the codebase.
bot_db = client[CONFIG["DB"]["bot_db"]]

# Collection Access
# ------------------------------
# Here you can define access to various collections within the bot's database.
# Each collection represents a distinct type of data.
# Example:
# logs_collection = bot_db["logs"]  # The 'logs' collection, used for storing log data


def get_mongo_client() -> MongoClient:
    """
    Returns the MongoClient instance for interacting with MongoDB.

    This function provides access to the MongoDB client that was initialized
    at the start of the module. It's useful when you need to perform operations
    with the database from other parts of your codebase without directly
    instantiating the client again.

    Returns:
        MongoClient: The MongoClient instance initialized with the URI and server API version.

    Example:
        To retrieve the client and access the database:

        ```
        client = get_mongo_client()
        database = client["my_database"]
        ```
    """
    return client
