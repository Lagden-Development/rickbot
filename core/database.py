"""
RickBot 2.0 - Database Layer

Type-safe MongoDB integration using Motor with repository pattern.
"""

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from typing import TypeVar, Generic, Type, Optional
from pydantic import BaseModel
import logging

from core.models import CommandLog, ErrorLog, MetricSnapshot, GuildSettings
from core.config import MongoDBConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class Repository(Generic[T]):
    """Type-safe repository for MongoDB collections"""

    def __init__(self, collection: AsyncIOMotorCollection, model: Type[T]):
        self.collection = collection
        self.model = model

    async def find_one(self, filter: dict) -> Optional[T]:
        """
        Find single document.

        Args:
            filter: MongoDB filter query

        Returns:
            Document if found, None otherwise
        """
        doc = await self.collection.find_one(filter)
        return self.model(**doc) if doc else None

    async def find_many(
        self,
        filter: dict,
        limit: int = 100,
        skip: int = 0,
        sort: Optional[list[tuple[str, int]]] = None,
    ) -> list[T]:
        """
        Find multiple documents.

        Args:
            filter: MongoDB filter query
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: Sort specification (e.g., [("created_at", -1)])

        Returns:
            List of matching documents
        """
        cursor = self.collection.find(filter).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        docs = await cursor.to_list(length=limit)
        return [self.model(**doc) for doc in docs]

    async def insert_one(self, document: T) -> str:
        """
        Insert document.

        Args:
            document: Pydantic model instance to insert

        Returns:
            Inserted document ID as string
        """
        result = await self.collection.insert_one(
            document.model_dump(by_alias=True, exclude_none=True)
        )
        return str(result.inserted_id)

    async def update_one(self, filter: dict, update: dict) -> bool:
        """
        Update document.

        Args:
            filter: MongoDB filter query
            update: Update data (will be wrapped in $set)

        Returns:
            True if document was modified, False otherwise
        """
        result = await self.collection.update_one(filter, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, filter: dict) -> bool:
        """
        Delete document.

        Args:
            filter: MongoDB filter query

        Returns:
            True if document was deleted, False otherwise
        """
        result = await self.collection.delete_one(filter)
        return result.deleted_count > 0

    async def count(self, filter: dict = {}) -> int:
        """
        Count documents matching filter.

        Args:
            filter: MongoDB filter query

        Returns:
            Count of matching documents
        """
        return await self.collection.count_documents(filter)

    async def aggregate(self, pipeline: list[dict]) -> list[dict]:
        """
        Run aggregation pipeline.

        Args:
            pipeline: MongoDB aggregation pipeline

        Returns:
            List of aggregation results
        """
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)


class Database:
    """Database manager with all repositories"""

    def __init__(self, client: AsyncIOMotorClient, config: MongoDBConfig):
        """
        Initialize database manager.

        Args:
            client: Motor async client
            config: MongoDB configuration
        """
        self.client = client
        self.db: AsyncIOMotorDatabase = client[config.database]
        self.config = config

        # Initialize repositories
        self.command_logs = Repository(
            self.db[config.command_logs_collection], CommandLog
        )
        self.error_logs = Repository(self.db[config.error_logs_collection], ErrorLog)
        self.metrics = Repository(self.db[config.metrics_collection], MetricSnapshot)
        self.guild_settings = Repository(
            self.db[config.guild_settings_collection], GuildSettings
        )

    async def ensure_indexes(self) -> None:
        """Create database indexes for optimal query performance"""
        logger.debug("Creating database indexes...")

        # Command logs indexes
        await self.command_logs.collection.create_index([("command_name", 1)])
        await self.command_logs.collection.create_index([("executed_at", -1)])
        await self.command_logs.collection.create_index([("user_id", 1)])
        await self.command_logs.collection.create_index([("guild_id", 1)])
        await self.command_logs.collection.create_index([("error_reference", 1)])

        # Error logs indexes
        await self.error_logs.collection.create_index(
            [("error_reference", 1)], unique=True
        )
        await self.error_logs.collection.create_index([("occurred_at", -1)])
        await self.error_logs.collection.create_index([("resolved", 1)])
        await self.error_logs.collection.create_index([("command_name", 1)])

        # Metrics indexes
        await self.metrics.collection.create_index([("snapshot_at", -1)])

        # Guild settings indexes
        await self.guild_settings.collection.create_index(
            [("guild_id", 1)], unique=True
        )

        logger.debug("Database indexes created successfully")

    async def close(self) -> None:
        """Close database connection"""
        self.client.close()
        logger.info("Database connection closed")
