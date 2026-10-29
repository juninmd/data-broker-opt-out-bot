from typing import Dict, Optional
from cryptography.fernet import Fernet
from data_broker_bot.config import get_encryption_key

PII_FIELDS = ("name", "email", "phone", "cpf")


def _get_fernet(key: Optional[str] = None) -> Fernet:
    key_str = key or get_encryption_key()
    return Fernet(key_str.encode("utf-8") if isinstance(key_str, str) else key_str)


def encrypt_field(value: Optional[str], key: Optional[str] = None) -> Optional[str]:
    """Encrypt a single plaintext string field using Fernet key."""
    if value is None:
        return None
    fernet = _get_fernet(key)
    return fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_field(ciphertext: Optional[str], key: Optional[str] = None) -> Optional[str]:
    """Decrypt a single Fernet ciphertext field into plaintext."""
    if ciphertext is None:
        return None
    fernet = _get_fernet(key)
    return fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")


def encrypt_pii(pii: Dict[str, Optional[str]], key: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Encrypt a dictionary of PII fields (name, email, phone, cpf)."""
    encrypted = {}
    for field in PII_FIELDS:
        if field in pii:
            val = pii[field]
            encrypted[field] = encrypt_field(val, key) if val is not None else None
    return encrypted


def decrypt_pii(pii: Dict[str, Optional[str]], key: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Decrypt a dictionary of encrypted PII fields (name, email, phone, cpf)."""
    decrypted = {}
    for field in PII_FIELDS:
        if field in pii:
            val = pii[field]
            decrypted[field] = decrypt_field(val, key) if val is not None else None
    return decrypted
