"""
RickBot 2.0 - Database Models

Type-safe Pydantic models for all MongoDB documents.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime, timezone


class Document(BaseModel):
    """Base document with MongoDB _id handling"""

    id: Optional[str] = Field(default=None, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CommandLog(Document):
    """Log entry for every command execution"""

    # Command info
    command_name: str
    command_type: Literal["slash", "context_menu_user", "context_menu_message"]

    # Execution info
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float  # How long it took
    success: bool

    # User info
    user_id: int
    user_name: str

    # Context info
    guild_id: Optional[int] = None
    guild_name: Optional[str] = None
    channel_id: Optional[int] = None
    channel_name: Optional[str] = None

    # Command data (optional - PII warning)
    arguments: Optional[dict[str, Any]] = None

    # Error reference (if failed)
    error_reference: Optional[str] = None


class ErrorLog(Document):
    """Detailed error log with unique reference"""

    # Error reference (shown to users)
    error_reference: str = Field(..., description="Unique error code shown to users")

    # Error info
    error_type: str
    error_message: str
    traceback: Optional[str] = None

    # When it happened
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Where it happened
    command_name: Optional[str] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    user_id: Optional[int] = None

    # Context
    interaction_data: Optional[dict[str, Any]] = None

    # Resolution tracking
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class MetricSnapshot(Document):
    """Periodic metric snapshots for trend analysis"""

    snapshot_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Bot stats
    guild_count: int
    user_count: int  # Approx from cached guilds
    uptime_seconds: float

    # Command stats (aggregated)
    total_commands_executed: int
    commands_by_name: dict[str, int]
    average_command_time_ms: dict[str, float]

    # Error stats
    total_errors: int
    errors_by_type: dict[str, int]

    # Memory/performance
    memory_usage_mb: Optional[float] = None


class GuildSettings(Document):
    """Guild-specific settings"""

    guild_id: int = Field(..., description="Discord guild ID")

    # Permissions
    admin_role_ids: list[int] = Field(default_factory=list)
    moderator_role_ids: list[int] = Field(default_factory=list)

    # Feature toggles
    disabled_commands: list[str] = Field(default_factory=list)

    # Custom data (extensible for user additions)
    custom_data: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
