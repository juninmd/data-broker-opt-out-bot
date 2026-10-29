import threading
from typing import Set

class UserStorage:
    def __init__(self):
        self._active_users: Set[int] = set()
        self._lock = threading.Lock()

    def add_user(self, user_id: int) -> None:
        with self._lock:
            self._active_users.add(user_id)

    def remove_user(self, user_id: int) -> None:
        with self._lock:
            self._active_users.discard(user_id)

    def get_active_users(self) -> Set[int]:
        with self._lock:
            return set(self._active_users)
