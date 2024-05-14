# Imports
from datetime import datetime
from db import money_collection
from typing import Union
import discord
import aiohttp

# Constants

TRANSACTION_LOG_WEBHOOK = "https://discord.com/api/webhooks/1238086897671208970/QdnFSb1sRPR3mEKHe7bEmcxAtvhov-XZFfRJs-_nZkOF_k_Z1IZ55p6bTnEPHVn0CxKp"
MAIN_EMBED_COLOR = 0x6D28D9
ERROR_EMBED_COLOR = 0x7C1719
SUCCESS_EMBED_COLOR = 0x1E8449

# Error Classes


class DatabaseImpossibleError(Exception):
    """Raised when an error that should'nt be possible occurs in the database."""

    pass


class MoneyTransactionLogError(Exception):
    """Raised when a money transaction log fails."""

    pass


# Functions


def user_balance(
    user_id: int,
    adjust_wallet: Union[int, None] = None,
    adjust_bank: Union[int, None] = None,
) -> Union[tuple[int, int], None]:
    """
    Update user's balance in the database and return the new balances.
    Will return the user's balance always.
    """
    query = money_collection.find_one({"_id": user_id})
    if not query:
        money_collection.insert_one({"_id": user_id, "wallet": 0, "bank": 0})
        query = money_collection.find_one({"_id": user_id})
        if not query:
            raise DatabaseImpossibleError(
                f"User with ID {user_id} not found in the database."
            )
    user: dict = query

    if not adjust_wallet and not adjust_bank:
        return user["wallet"], user["bank"]

    # Adjust the wallet or bank balance if needed
    if adjust_wallet:
        user["wallet"] += adjust_wallet
    if adjust_bank:
        user["bank"] += adjust_bank

    # Update the user's balance in the database
    money_collection.update_one(
        {"_id": user_id},
        {"$set": {"wallet": user["wallet"], "bank": user["bank"]}},
    )

    return user["wallet"], user["bank"]


def format_money(amount: int) -> str:
    return f"${amount:,}"


def format_time(seconds: int) -> str:
    """
    A function to format seconds into a human-readable format.

    Only output the highest time unit that is not zero.

    Example:
    3660 seconds -> 1 hour 1 minute
    300 seconds -> 5 minutes
    299 seconds -> 4 minutes 59 seconds
    30 seconds -> 30 seconds
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Prepare the output based on the largest time unit that's not zero
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0 and not time_parts:
        time_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    return " ".join(time_parts)


async def log_money_transaction(transaction_parts: list) -> None:
    """
    Log a money transaction in a channel using an embed and webhook.

    The transaction_parts list will be formatted as follows:
    [
        {
            "users": {"from": (discord user object), "to": (discord user object)},
            "movement": {"from": "wallet" | "bank", "to": "wallet" | "bank"},
            "amount": (int),
            "reason": (str),
        },
        ...
    ]
    """

    # Build the embed based on the transaction parts
    embed = discord.Embed(
        title="Money Transaction",
        color=MAIN_EMBED_COLOR,
        timestamp=datetime.utcnow(),
    )

    for part in transaction_parts:
        from_user: Union[discord.User, discord.Member] = part["users"]["from"]
        to_user: Union[discord.User, discord.Member] = part["users"]["to"]
        from_movement: str = part["movement"]["from"]
        to_movement: str = part["movement"]["to"]
        amount: int = part["amount"]
        reason: str = part["reason"]

        embed.add_field(
            name=(
                f"{from_user}'s {from_movement.capitalize()} -> {to_user}'s {to_movement.capitalize()}"
                if from_user != to_user
                else f"{from_user}'s {from_movement.capitalize()} to {to_movement.capitalize()}"
            ),
            value=f"Amount: {format_money(amount)}\nReason: {reason}",
            inline=False,
        )

    embed.set_footer(text="Better Hood Money")

    # Send the embed to the transaction log channel
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(TRANSACTION_LOG_WEBHOOK, session=session)

        try:
            await webhook.send(
                username="BHB Transaction Logs",
                allowed_mentions=discord.AllowedMentions.none(),
                embed=embed,
            )
        except discord.errors.NotFound:
            raise MoneyTransactionLogError(
                "The transaction log channel webhook was not found."
            )
        except discord.errors.Forbidden:
            raise MoneyTransactionLogError(
                "The bot does not have permission to send messages in the transaction log channel."
            )
        except discord.errors.HTTPException:
            raise MoneyTransactionLogError(
                "An HTTP exception occurred while sending the transaction log."
            )
        except Exception:
            raise MoneyTransactionLogError(
                "An unknown exception occurred while sending the transaction log."
            )
