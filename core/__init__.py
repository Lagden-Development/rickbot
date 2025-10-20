"""
RickBot 2.0 - Core Package

Production-grade Discord bot framework with database-first observability.
"""

from core.bot import RickBot
from core.config import Config
from core.database import Database, Repository
from core.observability import ObservabilityTracker
from core.models import CommandLog, ErrorLog, MetricSnapshot, GuildSettings

__version__ = "2.0.0"

__all__ = [
    "RickBot",
    "Config",
    "Database",
    "Repository",
    "ObservabilityTracker",
    "CommandLog",
    "ErrorLog",
    "MetricSnapshot",
    "GuildSettings",
]
