"""Telegram messaging transport adapter."""
import os
import urllib.request
import urllib.parse
import json
import logging
from typing import Optional, Dict, Any, List
from src.adapters.base import BaseAdapter
from src.models import Message, TransportType

logger = logging.getLogger(__name__)


class TelegramAdapter(BaseAdapter):
    """Adapter for Telegram Bot API."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        api_url: Optional[str] = None,
        mock_mode: bool = False
    ):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.mock_mode = mock_mode or not self.bot_token
        self.api_url = api_url or f"https://api.telegram.org/bot{self.bot_token}"
        self.sent_messages: List[Dict[str, Any]] = []

    @property
    def transport_type(self) -> TransportType:
        return TransportType.TELEGRAM

    def parse_incoming(self, payload: Dict[str, Any]) -> Optional[Message]:
        """Parse incoming Telegram update payload."""
        if not isinstance(payload, dict):
            return None

        message_data = payload.get("message") or payload.get("edited_message")
        if not message_data:
            return None

        sender = message_data.get("from", {})
        sender_id = str(sender.get("id", ""))
        chat = message_data.get("chat", {})
        recipient_id = str(chat.get("id", sender_id))
        text = message_data.get("text", "").strip()

        if not sender_id or not text:
            return None

        return Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            transport=TransportType.TELEGRAM,
            text=text,
            timestamp=float(message_data.get("date", 0)),
            raw_payload=payload
        )

    def format_outgoing(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """Format outgoing Telegram sendMessage payload."""
        return {
            "chat_id": recipient_id,
            "text": text,
            "parse_mode": "HTML"
        }

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send message via Telegram API."""
        payload = self.format_outgoing(recipient_id, text)
        self.sent_messages.append(payload)

        if self.mock_mode:
            logger.info(f"[Telegram Mock Send] to {recipient_id}: {text}")
            return True

        url = f"{self.api_url}/sendMessage"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
