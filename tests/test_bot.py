import pytest
from data_broker_bot.adapters.base import BaseAdapter
from data_broker_bot.bot import OptOutBot
from data_broker_bot.config import generate_key


def test_bot_full_workflow(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    bot = OptOutBot()
    bot.register_user(
        user_id="bot_user_1",
        name="Pedro Rocha",
        email="pedro@example.com",
        phone="+5511911112222",
        cpf="11122233344",
    )

    user_fetched = bot.get_user("bot_user_1")
    assert user_fetched is not None
    # Verify PII fields stored/retrieved from bot are ciphertext
    assert user_fetched.pii_fields["name"].startswith("gAAAAA")
    assert user_fetched.pii_fields["email"].startswith("gAAAAA")

    # Submit opt-out
    adapter = BaseAdapter("DataBrokerX")
    submission = bot.submit_opt_out("bot_user_1", adapter=adapter)

    assert submission["status"] == "submitted"
    assert submission["broker"] == "DataBrokerX"
    assert submission["submitted_pii"]["email"] == "pedro@example.com"
    assert submission["submitted_pii"]["cpf"] == "11122233344"


def test_submit_nonexistent_user_raises_error(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    bot = OptOutBot()
    with pytest.raises(ValueError, match="User with id nonexistent not found"):
        bot.submit_opt_out("nonexistent")
