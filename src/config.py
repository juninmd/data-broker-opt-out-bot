import os
from typing import Set

class Config:
    def __init__(self):
        self.bot_token: str = os.getenv("BOT_TOKEN", "")
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.admin_ids: Set[int] = {
            int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()
        }

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids
