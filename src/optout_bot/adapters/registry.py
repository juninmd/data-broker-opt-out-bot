"""Adapter registry and plugin discovery using standard setuptools entry points."""

import importlib.metadata
import logging
from typing import Dict, Type, Optional

from optout_bot.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

ENTRY_POINT_GROUP = "optout_bot.adapters"


class AdapterRegistry:
    """Registry that manages data broker adapters discovered via entry points or direct registration."""

    def __init__(self) -> None:
        self._adapters: Dict[str, Type[BaseAdapter]] = {}

    def register(self, adapter_cls: Type[BaseAdapter]) -> None:
        """Manually register an adapter class."""
        if not isinstance(adapter_cls, type) or not issubclass(adapter_cls, BaseAdapter):
            raise TypeError(f"{adapter_cls} must be a subclass of BaseAdapter")

        # Access broker_id via property or class descriptor safely without instantiating
        broker_id = getattr(adapter_cls, "broker_id", None)
        if callable(broker_id):
            # If broker_id is a function/classmethod
            broker_id = broker_id()
        elif isinstance(broker_id, property):
            # Try getting broker_id from a temporary instance if zero-arg constructor exists,
            # fallback to broker_id.fget(None) if supported or instantiate
            try:
                temp_instance = adapter_cls()
                broker_id = temp_instance.broker_id
            except Exception as err:
                raise ValueError(f"Could not inspect broker_id from {adapter_cls.__name__}: {err}")

        if not broker_id or not isinstance(broker_id, str):
            raise ValueError(f"Adapter class {adapter_cls.__name__} must provide a valid broker_id string.")

        self._adapters[broker_id] = adapter_cls
        logger.info(f"Registered adapter for broker_id: '{broker_id}'")

    def discover_plugins(self) -> None:
        """Discover and load installed community adapter plugins from standard setuptools entry points."""
        try:
            eps = importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)
        except Exception as err:
            logger.warning(f"Error loading entry points for {ENTRY_POINT_GROUP}: {err}")
            return

        for ep in eps:
            try:
                plugin_obj = ep.load()
                if isinstance(plugin_obj, type) and issubclass(plugin_obj, BaseAdapter):
                    self.register(plugin_obj)
                else:
                    logger.warning(
                        f"Entry point '{ep.name}' ({ep.value}) did not resolve to a valid BaseAdapter subclass."
                    )
            except Exception as err:
                logger.error(f"Failed to load plugin entry point '{ep.name}': {err}")

    def get_adapter_class(self, broker_id: str) -> Optional[Type[BaseAdapter]]:
        """Retrieve the adapter class for a given broker_id."""
        return self._adapters.get(broker_id)

    def list_adapters(self) -> Dict[str, Type[BaseAdapter]]:
        """List all currently registered adapter classes indexed by broker_id."""
        return dict(self._adapters)


# Global default registry instance
registry = AdapterRegistry()


def discover_adapters() -> AdapterRegistry:
    """Convenience helper to discover plugins and return the global registry."""
    registry.discover_plugins()
    return registry
