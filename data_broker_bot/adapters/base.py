from typing import Any, Dict, Optional
from data_broker_bot.crypto import decrypt_pii
from data_broker_bot.models import User


class BaseAdapter:
    def __init__(self, broker_name: str = "GenericBroker"):
        self.broker_name = broker_name

    def submit(self, user: User, key: Optional[str] = None) -> Dict[str, Any]:
        """Submit opt-out request for a user.

        Decrypts user.pii_fields ONLY inside this method right before submission.
        """
        plain_pii = decrypt_pii(user.pii_fields, key=key)

        if not plain_pii.get("email"):
            raise ValueError("User email is required for submission")

        # Adapter processing with decrypted PII
        return {
            "status": "submitted",
            "broker": self.broker_name,
            "user_id": user.user_id,
            "submitted_pii": plain_pii,
        }
