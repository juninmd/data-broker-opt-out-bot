from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class User:
    user_id: str
    pii_fields: Dict[str, Optional[str]] = field(default_factory=dict)
    created_at: Optional[str] = None

    @classmethod
    def create(
        cls,
        user_id: str,
        name: str,
        email: str,
        phone: str,
        cpf: str,
        key: Optional[str] = None,
    ) -> "User":
        """Factory method to construct a User with PII fields encrypted."""
        from data_broker_bot.crypto import encrypt_pii

        raw_pii = {"name": name, "email": email, "phone": phone, "cpf": cpf}
        encrypted_pii = encrypt_pii(raw_pii, key=key)
        return cls(user_id=user_id, pii_fields=encrypted_pii)
