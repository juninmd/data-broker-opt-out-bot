import os
from cryptography.fernet import Fernet


def get_encryption_key() -> str:
    """Retrieve the PII encryption key from environment variable."""
    key = os.environ.get("PII_ENCRYPTION_KEY")
    if not key:
        raise ValueError("PII_ENCRYPTION_KEY environment variable is not set")
    return key


def generate_key() -> str:
    """Generate a new Fernet encryption key as a string."""
    return Fernet.generate_key().decode("utf-8")
