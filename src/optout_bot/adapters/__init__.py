"""Adapters package for data broker opt-out functionality."""

from optout_bot.adapters.base import BaseAdapter
from optout_bot.adapters.registry import AdapterRegistry, discover_adapters, registry

__all__ = ["BaseAdapter", "AdapterRegistry", "discover_adapters", "registry"]
