"""Data models for transport adapters and message handling."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import time


class TransportType(str, Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"


@dataclass
class Message:
    sender_id: str
    recipient_id: str
    transport: TransportType
    text: str
    timestamp: float = field(default_factory=time.time)
    raw_payload: Optional[Dict[str, Any]] = None


@dataclass
class UserAccount:
    user_id: str
    telegram_id: Optional[str] = None
    whatsapp_id: Optional[str] = None
    opted_in_whatsapp: bool = False
    link_token: Optional[str] = None
