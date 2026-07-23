"""Append-only sink for the learning dataset's *testimony* layer."""

from .event_log import EventLog, NullEventLog

__all__ = ["EventLog", "NullEventLog"]
