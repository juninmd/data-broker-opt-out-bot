"""XYZ Data Broker Community Adapter."""

from typing import Any, Dict
from optout_bot.adapters.base import BaseAdapter


class XYZBrokerAdapter(BaseAdapter):
    """Sample community adapter for broker 'XYZ Data Broker'."""

    @property
    def broker_id(self) -> str:
        return "optout_broker_xyz"

    @property
    def name(self) -> str:
        return "XYZ Data Broker"

    def submit_opt_out(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        email = user_data.get("email", "unknown")
        # Sample logic for handling opt-out request
        return {
            "status": "submitted",
            "confirmation_id": f"xyz-optout-{email}-12345",
            "message": f"Successfully submitted opt-out for {email} to XYZ Data Broker",
        }

    def check_status(self, confirmation_id: str) -> Dict[str, Any]:
        return {
            "confirmation_id": confirmation_id,
            "status": "processed",
            "details": "Opt-out confirmed by XYZ Data Broker.",
        }
