import pytest
from data_broker_bot.adapters.base import BaseAdapter
from data_broker_bot.config import generate_key
from data_broker_bot.models import User


def test_adapter_submit_decrypts_pii(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    user = User.create(
        user_id="u_adapter",
        name="Maria Santos",
        email="maria@example.com",
        phone="+5511988887777",
        cpf="99988877700",
    )

    # Ensure user object holds encrypted PII
    assert user.pii_fields["email"].startswith("gAAAAA")

    adapter = BaseAdapter(broker_name="Serasa")
    result = adapter.submit(user)

    assert result["status"] == "submitted"
    assert result["broker"] == "Serasa"
    assert result["user_id"] == "u_adapter"
    assert result["submitted_pii"]["name"] == "Maria Santos"
    assert result["submitted_pii"]["email"] == "maria@example.com"
    assert result["submitted_pii"]["phone"] == "+5511988887777"
    assert result["submitted_pii"]["cpf"] == "99988877700"


def test_adapter_submit_requires_email(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    user = User.create(
        user_id="u_no_email",
        name="No Email",
        email="",
        phone="123",
        cpf="456",
    )

    adapter = BaseAdapter()
    with pytest.raises(ValueError, match="User email is required"):
        adapter.submit(user)
