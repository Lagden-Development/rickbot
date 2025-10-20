"""
RickBot 2.0 - Configuration System

Type-safe configuration using Pydantic with YAML support and environment variable substitution.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from pathlib import Path
import yaml
import os
import re
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class IntentsConfig(BaseModel):
    """Discord intents configuration with validation"""

    guilds: bool = True
    members: bool = False  # Privileged
    message_content: bool = False  # Privileged - not needed for slash only
    presences: bool = False  # Privileged
    guild_messages: bool = True
    dm_messages: bool = True
    guild_reactions: bool = False
    dm_reactions: bool = False
    guild_typing: bool = False
    dm_typing: bool = False
    voice_states: bool = False
    integrations: bool = True
    webhooks: bool = False
    invites: bool = False
    auto_moderation: bool = False
    auto_moderation_configuration: bool = False
    auto_moderation_execution: bool = False
    polls: bool = False

    @field_validator("members", "message_content", "presences")
    @classmethod
    def warn_privileged(cls, v: bool, info) -> bool:
        """Warn about privileged intents"""
        if v:
            print(
                f"⚠️  Privileged intent '{info.field_name}' enabled - ensure it's activated in Discord Portal"
            )
        return v


class MongoDBConfig(BaseModel):
    """MongoDB configuration"""

    uri: str = Field(..., description="MongoDB connection URI")
    database: str = Field(..., description="Database name")
    pool_size: int = Field(default=10, ge=1, le=100)
    timeout_ms: int = Field(default=5000, ge=1000)
    retry_writes: bool = True

    # Collection names (configurable)
    command_logs_collection: str = "command_logs"
    error_logs_collection: str = "error_logs"
    metrics_collection: str = "metrics"
    guild_settings_collection: str = "guild_settings"


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    format: Literal["text", "json"] = "text"
    file: Optional[Path] = None
    rotation: str = "100 MB"
    log_discord_library: bool = False  # Log discord.py internals


class ObservabilityConfig(BaseModel):
    """Observability settings - all DB-based"""

    track_command_execution: bool = True
    track_command_timing: bool = True
    track_command_args: bool = True  # Log command arguments (PII warning)
    track_errors: bool = True
    error_reference_length: int = 6  # Length of error codes (e.g., ERR-A7K9X2)
    store_error_traceback: bool = True
    aggregate_metrics_interval: int = 300  # Seconds between metric snapshots


class BotConfig(BaseModel):
    """Bot configuration"""

    token: str = Field(..., description="Discord bot token (use env var)")
    application_id: int = Field(..., description="Discord application ID")
    dev_guild_id: Optional[int] = Field(
        default=None, description="Guild ID for testing commands (syncs instantly)"
    )
    owner_ids: list[int] = Field(default_factory=list)
    status_text: str = "Ready for commands"
    status_type: Literal["playing", "watching", "listening", "competing"] = "playing"
    sync_commands_on_ready: bool = True  # Auto-sync slash commands


class Config(BaseModel):
    """Root configuration model with environment variable support"""

    bot: BotConfig
    intents: IntentsConfig
    mongodb: MongoDBConfig
    logging: LoggingConfig
    observability: ObservabilityConfig

    @classmethod
    def detect_environment(cls) -> Environment:
        """
        Detect current environment from environment variables.

        Checks BOT_ENV, ENVIRONMENT, or NODE_ENV variables.
        Defaults to DEVELOPMENT if not set.

        Returns:
            Environment enum value
        """
        env_var = (
            os.getenv("BOT_ENV") or os.getenv("ENVIRONMENT") or os.getenv("NODE_ENV")
        )

        if env_var:
            env_lower = env_var.lower()
            if "prod" in env_lower:
                return Environment.PRODUCTION
            elif "stag" in env_lower:
                return Environment.STAGING
            else:
                return Environment.DEVELOPMENT
        else:
            # Default to development
            return Environment.DEVELOPMENT

    def validate_production_config(self) -> list[str]:
        """
        Validate configuration for production deployment.

        Returns:
            List of warning messages (empty if all checks pass)
        """
        warnings = []

        # Check for dev-only settings
        if self.bot.dev_guild_id is not None:
            warnings.append(
                "WARNING: dev_guild_id is set - commands will only sync to that guild. "
                "Set to null for global production deployment."
            )

        # Check for dangerous observability settings
        if self.observability.track_command_args:
            warnings.append(
                "WARNING: track_command_args is enabled - this may log sensitive user data (PII). "
                "Consider setting to false in production."
            )

        if self.logging.level == "DEBUG":
            warnings.append(
                "WARNING: Logging level is DEBUG - this is verbose and may impact performance. "
                "Consider using INFO or WARNING in production."
            )

        if self.logging.log_discord_library:
            warnings.append(
                "WARNING: log_discord_library is enabled - this creates very verbose logs. "
                "Disable in production."
            )

        # Check MongoDB settings
        if "localhost" in self.mongodb.uri or "127.0.0.1" in self.mongodb.uri:
            warnings.append(
                "WARNING: MongoDB URI points to localhost - ensure this is intentional for production. "
                "Consider using a managed service like MongoDB Atlas."
            )

        # Check if default database name
        if self.mongodb.database == "rickbot":
            warnings.append(
                "INFO: Using default database name 'rickbot'. "
                "Consider using environment-specific names (e.g., 'rickbot_prod')."
            )

        # Check for missing owner IDs
        if not self.bot.owner_ids:
            warnings.append(
                "WARNING: No owner_ids configured - owner-only commands will not work. "
                "Add your user ID to bot.owner_ids."
            )

        return warnings

    @classmethod
    def load(cls, path: str | Path = "config.yaml") -> "Config":
        """
        Load and validate configuration from YAML with env var substitution.

        Supports ${ENV_VAR} syntax for environment variables.
        Automatically detects environment and validates production settings.

        Args:
            path: Path to the YAML configuration file

        Returns:
            Validated Config instance

        Raises:
            ValueError: If required environment variables are missing
            FileNotFoundError: If config file doesn't exist
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path) as f:
            content = f.read()

        # Replace ${ENV_VAR} with environment variables
        def replace_env(match):
            env_var = match.group(1)
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(
                    f"Environment variable {env_var} not found. "
                    f"Please set it in your environment or .env file."
                )
            return value

        content = re.sub(r"\$\{([^}]+)\}", replace_env, content)
        data = yaml.safe_load(content)

        logger.debug(f"Loaded configuration from {path}")
        config = cls(**data)

        # Detect environment and validate
        env = cls.detect_environment()
        logger.info(f"Detected environment: {env.value}")

        # Validate production configuration
        if env == Environment.PRODUCTION:
            warnings = config.validate_production_config()
            if warnings:
                logger.warning("=" * 70)
                logger.warning("PRODUCTION CONFIGURATION WARNINGS")
                logger.warning("=" * 70)
                for warning in warnings:
                    logger.warning(f"  • {warning}")
                logger.warning("=" * 70)
                logger.warning(
                    "Review these warnings before deploying to production. "
                    "Set BOT_ENV=development to suppress these warnings in dev."
                )

        return config

    @staticmethod
    def save_template(path: str | Path = "config.yaml") -> None:
        """
        Save a template config file with sensible defaults.

        Args:
            path: Path where to save the template
        """
        template = {
            "bot": {
                "token": "${DISCORD_TOKEN}",
                "application_id": 123456789012345678,
                "dev_guild_id": None,
                "owner_ids": [],
                "status_text": "Ready for commands",
                "status_type": "playing",
                "sync_commands_on_ready": True,
            },
            "intents": {
                "guilds": True,
                "members": False,
                "message_content": False,
                "presences": False,
                "guild_messages": True,
                "dm_messages": True,
                "voice_states": False,
            },
            "mongodb": {
                "uri": "${MONGO_URI}",
                "database": "rickbot",
                "pool_size": 10,
                "timeout_ms": 5000,
                "retry_writes": True,
            },
            "logging": {
                "level": "INFO",
                "format": "text",
                "file": None,
                "log_discord_library": False,
            },
            "observability": {
                "track_command_execution": True,
                "track_command_timing": True,
                "track_command_args": True,
                "track_errors": True,
                "error_reference_length": 6,
                "store_error_traceback": True,
                "aggregate_metrics_interval": 300,
            },
        }

        with open(path, "w") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Created template configuration at {path}")
        print(f"✅ Configuration template created at {path}")
        print(
            "📝 Edit this file and set your environment variables before starting the bot"
        )
