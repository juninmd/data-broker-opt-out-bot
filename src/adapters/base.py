"""Base adapter interface for messaging transports."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.models import Message, TransportType


class BaseAdapter(ABC):
    """Abstract Base Adapter for message transports (Telegram, WhatsApp, etc.)."""

    @property
    @abstractmethod
    def transport_type(self) -> TransportType:
        """Return transport type identifier."""
        pass

    @abstractmethod
    def parse_incoming(self, payload: Dict[str, Any]) -> Optional[Message]:
        """Parse raw incoming payload into a standardized Message object."""
        pass

    @abstractmethod
    def format_outgoing(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """Format outbound message payload according to target platform API."""
        pass

    @abstractmethod
    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send message to recipient on target platform."""
        pass

    def verify_webhook(self, headers: Dict[str, str], body: bytes) -> bool:
        """Verify authenticity of webhook payload signature if required by platform."""
        return True
