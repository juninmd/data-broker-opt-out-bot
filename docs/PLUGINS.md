# Community Adapter Plugin Guide

This document specifies the entry-point interface and architectural guidelines for building and distributing community adapters for `data-broker-opt-out-bot`.

## Architectural Overview

`data-broker-opt-out-bot` uses Python standard entry points (via `importlib.metadata`) to discover and automatically load community adapters installed in the environment.

When an adapter package (e.g. `optout-broker-xyz`) is installed via `pip install`, its declared entry point auto-registers it with the central `AdapterRegistry`.

---

## Entry-Point Specification

Every adapter plugin package must declare an entry point under the group `optout_bot.adapters` in its `pyproject.toml` (or `setup.cfg`):

```toml
[project.entry-points."optout_bot.adapters"]
your_broker_id = "your_package_module.adapter:YourAdapterClass"
```

### Constraints & Standards
1. **Entry Point Group**: Must be `"optout_bot.adapters"`.
2. **Class Interface**: The referenced entry-point class must inherit from `optout_bot.adapters.BaseAdapter`.
3. **Broker ID**: `broker_id` must return a unique string identifier across the ecosystem (e.g., `optout_broker_xyz`).

---

## Implementing `BaseAdapter`

All adapters must implement the four required abstract members of `BaseAdapter`:

```python
from typing import Any, Dict
from optout_bot.adapters import BaseAdapter


class MyBrokerAdapter(BaseAdapter):

    @property
    def broker_id(self) -> str:
        """Unique identifier string for the broker."""
        return "my_broker"

    @property
    def name(self) -> str:
        """Human-readable display name for the data broker."""
        return "My Data Broker"

    def submit_opt_out(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submits opt-out request for a given user dict.

        Must return a dict containing status and optional tracking metadata.
        """
        # Submission logic here...
        return {
            "status": "submitted",
            "confirmation_id": "REQ-12345",
        }

    def check_status(self, confirmation_id: str) -> Dict[str, Any]:
        """Checks status of a previously submitted opt-out request."""
        # Status verification logic here...
        return {
            "confirmation_id": confirmation_id,
            "status": "completed",
        }
```

---

## Sample Template Repository

A complete template repository is available under [`examples/sample-plugin`](../examples/sample-plugin).

### Quickstart for Plugin Authors

1. Clone or copy `examples/sample-plugin`.
2. Renaming `optout_broker_xyz` to your plugin package name.
3. Update `pyproject.toml` entry-point definition.
4. Test locally by running:
   ```bash
   pip install -e .
   pytest
   ```
