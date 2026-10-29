"""WhatsApp Meta Cloud API transport adapter."""
import os
import hmac
import hashlib
import json
import logging
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List
from src.adapters.base import BaseAdapter
from src.models import Message, TransportType

logger = logging.getLogger(__name__)


class WhatsAppAdapter(BaseAdapter):
    """Adapter for Meta Cloud API (WhatsApp Business API)."""

    def __init__(
        self,
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
        verify_token: Optional[str] = None,
        app_secret: Optional[str] = None,
        api_version: str = "v18.0",
        mock_mode: bool = False
    ):
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.access_token = access_token or os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.verify_token = verify_token or os.getenv("WHATSAPP_VERIFY_TOKEN", "")
        self.app_secret = app_secret or os.getenv("WHATSAPP_APP_SECRET", "")
        self.api_version = api_version
        self.mock_mode = mock_mode or not self.access_token
        self.sent_messages: List[Dict[str, Any]] = []

    @property
    def transport_type(self) -> TransportType:
        return TransportType.WHATSAPP

    def parse_incoming(self, payload: Dict[str, Any]) -> Optional[Message]:
        """Parse incoming Meta Cloud API WhatsApp message webhook payload."""
        if not isinstance(payload, dict):
            return None

        entries = payload.get("entry", [])
        if not entries or not isinstance(entries, list):
            return None

        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages or not isinstance(messages, list):
                    continue

                for msg in messages:
                    # Handle text messages
                    sender_id = str(msg.get("from", ""))
                    msg_type = msg.get("type")
                    text = ""
                    if msg_type == "text":
                        text = msg.get("text", {}).get("body", "").strip()
                    elif msg_type == "button":
                        text = msg.get("button", {}).get("text", "").strip()
                    elif msg_type == "interactive":
                        interactive = msg.get("interactive", {})
                        if interactive.get("type") == "button_reply":
                            text = interactive.get("button_reply", {}).get("title", "").strip()

                    if sender_id and text:
                        # Extract metadata if available
                        metadata = value.get("metadata", {})
                        recipient_id = metadata.get("phone_number_id", self.phone_number_id)
                        timestamp = float(msg.get("timestamp", 0))

                        return Message(
                            sender_id=sender_id,
                            recipient_id=recipient_id,
                            transport=TransportType.WHATSAPP,
                            text=text,
                            timestamp=timestamp,
                            raw_payload=payload
                        )

        return None

    def format_outgoing(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """Format outbound message for Meta Cloud API."""
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {
                "body": text
            }
        }

    def verify_webhook(self, headers: Dict[str, str], body: bytes) -> bool:
        """Verify Meta X-Hub-Signature-256 HMAC signature."""
        if not self.app_secret:
            # If no app secret is configured, skip signature check in unconfigured development mode
            logger.warning("WHATSAPP_APP_SECRET is not configured; skipping signature verification")
            return True

        # Case-insensitive header lookup
        signature_header = None
        for key, value in headers.items():
            if key.lower() == "x-hub-signature-256":
                signature_header = value
                break

        if not signature_header:
            logger.warning("Missing X-Hub-Signature-256 header")
            return False

        if not signature_header.startswith("sha256="):
            logger.warning("Invalid signature header format")
            return False

        expected_sig = signature_header[7:]
        computed_sig = hmac.new(
            self.app_secret.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_sig, expected_sig)

    def verify_challenge(self, mode: Optional[str], token: Optional[str], challenge: Optional[str]) -> Optional[str]:
        """Verify GET webhook setup challenge from Meta Cloud API."""
        if mode == "subscribe" and token and self.verify_token and token == self.verify_token:
            return challenge
        return None

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send message using Meta Graph API."""
        payload = self.format_outgoing(recipient_id, text)
        self.sent_messages.append(payload)

        if self.mock_mode:
            logger.info(f"[WhatsApp Mock Send] to {recipient_id}: {text}")
            return True

        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return False
