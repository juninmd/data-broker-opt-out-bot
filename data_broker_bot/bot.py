from typing import Any, Dict, List, Optional
from data_broker_bot.adapters.base import BaseAdapter
from data_broker_bot.db import Database
from data_broker_bot.models import User


class OptOutBot:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def register_user(
        self,
        user_id: str,
        name: str,
        email: str,
        phone: str,
        cpf: str,
        key: Optional[str] = None,
    ) -> User:
        """Register a new user in the system.

        PII fields are encrypted immediately upon creation and saved as ciphertext.
        """
        user = User.create(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            cpf=cpf,
            key=key,
        )
        self.db.save_user(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve user record. PII fields remain encrypted."""
        return self.db.get_user(user_id)

    def submit_opt_out(
        self,
        user_id: str,
        adapter: Optional[BaseAdapter] = None,
        key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit opt-out request for a registered user.

        Retrieves encrypted user from DB and delegates to adapter.submit(),
        which is the only place decryption takes place.
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        active_adapter = adapter or BaseAdapter()
        return active_adapter.submit(user, key=key)
