"""Core adapter abstractions and models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAdapter(ABC):
    """Abstract Base Class that all data broker opt-out adapters must implement."""

    @property
    @abstractmethod
    def broker_id(self) -> str:
        """Unique string identifier for the data broker (e.g. 'xyz_broker')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name of the data broker."""
        pass

    @abstractmethod
    def submit_opt_out(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit an opt-out request for a user.

        Args:
            user_data: Dictionary containing target user details (e.g., name, email, phone).

        Returns:
            Dict containing status information (e.g., {'status': 'submitted', 'confirmation_id': '...'}).
        """
        pass

    @abstractmethod
    def check_status(self, confirmation_id: str) -> Dict[str, Any]:
        """Check status of a previously submitted opt-out request.

        Args:
            confirmation_id: Unique request tracking ID.

        Returns:
            Dict containing status update details.
        """
        pass
