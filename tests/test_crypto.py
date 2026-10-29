import os
import pytest
from cryptography.fernet import InvalidToken
from data_broker_bot.config import generate_key, get_encryption_key
from data_broker_bot.crypto import (
    decrypt_field,
    decrypt_pii,
    encrypt_field,
    encrypt_pii,
)


def test_encryption_decryption_with_key():
    key = generate_key()
    plain = "test@example.com"
    encrypted = encrypt_field(plain, key=key)

    assert encrypted != plain
    assert encrypted.startswith("gAAAAA")

    decrypted = decrypt_field(encrypted, key=key)
    assert decrypted == plain


def test_encryption_decryption_with_env(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    pii = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+5511999998888",
        "cpf": "12345678901",
    }

    encrypted_pii = encrypt_pii(pii)
    for k, v in encrypted_pii.items():
        assert v != pii[k]
        assert v.startswith("gAAAAA")

    decrypted_pii = decrypt_pii(encrypted_pii)
    assert decrypted_pii == pii


def test_encryption_handles_none():
    assert encrypt_field(None) is None
    assert decrypt_field(None) is None


def test_missing_env_key_raises_error(monkeypatch):
    monkeypatch.delenv("PII_ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValueError, match="PII_ENCRYPTION_KEY environment variable is not set"):
        get_encryption_key()


def test_invalid_token_decryption_fails():
    key1 = generate_key()
    key2 = generate_key()
    encrypted = encrypt_field("secret", key=key1)

    with pytest.raises(InvalidToken):
        decrypt_field(encrypted, key=key2)
