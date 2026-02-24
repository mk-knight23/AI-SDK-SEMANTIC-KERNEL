"""
Time and date plugin for Semantic Kernel.

Provides current time, date, and time-related calculations.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from dateutil import parser as date_parser

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from app.plugins.base import BasePlugin, PluginMetadata


class TimePlugin(BasePlugin):
    """
    Plugin for time and date operations.

    Provides functions to get current time, parse dates, and
    perform time-based calculations.
    """

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="time",
            description="Provides current time, date, and time-related calculations",
            version="1.0.0",
            author="AI-SDK-SEMANTIC-KERNEL"
        )

    @kernel_function(
        description="Get the current date and time in ISO 8601 format",
        name="current_time"
    )
    def current_time(self) -> str:
        """
        Get the current date and time.

        Returns:
            Current UTC datetime in ISO 8601 format
        """
        return datetime.now(timezone.utc).isoformat()

    @kernel_function(
        description="Get the current date in YYYY-MM-DD format",
        name="current_date"
    )
    def current_date(self) -> str:
        """
        Get the current date.

        Returns:
            Current UTC date in YYYY-MM-DD format
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @kernel_function(
        description="Get the current time in HH:MM:SS format",
        name="current_time_only"
    )
    def current_time_only(self) -> str:
        """
        Get the current time.

        Returns:
            Current UTC time in HH:MM:SS format
        """
        return datetime.now(timezone.utc).strftime("%H:%M:%S")

    @kernel_function(
        description="Get the current Unix timestamp",
        name="current_timestamp"
    )
    def current_timestamp(self) -> int:
        """
        Get the current Unix timestamp.

        Returns:
            Current Unix timestamp (seconds since epoch)
        """
        return int(datetime.now(timezone.utc).timestamp())

    @kernel_function(
        description="Parse a date string and return ISO format",
        name="parse_date"
    )
    def parse_date(self, date_string: str) -> str:
        """
        Parse a date string and return in ISO format.

        Args:
            date_string: Date string to parse

        Returns:
            Parsed date in ISO 8601 format
        """
        try:
            parsed = date_parser.parse(date_string)
            return parsed.isoformat()
        except Exception:
            return f"Could not parse date: {date_string}"

    @kernel_function(
        description="Calculate the difference between two dates in days",
        name="date_diff"
    )
    def date_diff(self, date1: str, date2: str) -> str:
        """
        Calculate the difference between two dates.

        Args:
            date1: First date string
            date2: Second date string

        Returns:
            Difference in days as a string
        """
        try:
            d1 = date_parser.parse(date1)
            d2 = date_parser.parse(date2)
            diff = abs((d2 - d1).days)
            return f"{diff} days"
        except Exception as e:
            return f"Error calculating date difference: {str(e)}"

    @kernel_function(
        description="Add days to a date string",
        name="add_days"
    )
    def add_days(self, date_string: str, days: int) -> str:
        """
        Add days to a date.

        Args:
            date_string: Date string
            days: Number of days to add (can be negative)

        Returns:
            New date in ISO 8601 format
        """
        try:
            date = date_parser.parse(date_string)
            new_date = date + timedelta(days=days)
            return new_date.isoformat()
        except Exception as e:
            return f"Error adding days: {str(e)}"

    @kernel_function(
        description="Get day of week for a date",
        name="day_of_week"
    )
    def day_of_week(self, date_string: Optional[str] = None) -> str:
        """
        Get the day of the week for a date.

        Args:
            date_string: Date string (defaults to current date)

        Returns:
            Day of the week name
        """
        try:
            if date_string:
                date = date_parser.parse(date_string)
            else:
                date = datetime.now(timezone.utc)
            return date.strftime("%A")
        except Exception:
            return "Could not determine day of week"

    @kernel_function(
        description="Format a date string using a format string",
        name="format_date"
    )
    def format_date(self, date_string: str, format_string: str) -> str:
        """
        Format a date using a custom format string.

        Args:
            date_string: Date string to format
            format_string: strftime format string (e.g., '%B %d, %Y')

        Returns:
            Formatted date string
        """
        try:
            date = date_parser.parse(date_string)
            return date.strftime(format_string)
        except Exception as e:
            return f"Error formatting date: {str(e)}"
