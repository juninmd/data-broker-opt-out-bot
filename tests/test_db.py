import pytest
from data_broker_bot.config import generate_key
from data_broker_bot.db import Database
from data_broker_bot.models import User


def test_db_stores_pii_as_ciphertext(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    db = Database(":memory:")
    user = User.create(
        user_id="user_test_1",
        name="Carlos Silva",
        email="carlos@example.com",
        phone="+5511977776666",
        cpf="00011122233",
    )
    db.save_user(user)

    # Dump raw database contents to verify ciphertext
    dump = db.dump_db()
    assert len(dump) == 1
    row = dump[0]

    assert row["user_id"] == "user_test_1"
    for field_name in ("name", "email", "phone", "cpf"):
        assert row[field_name] is not None
        assert row[field_name] != user.pii_fields[field_name] or row[field_name].startswith("gAAAAA")
        assert row[field_name].startswith("gAAAAA")


def test_db_get_and_list_users(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("PII_ENCRYPTION_KEY", key)

    db = Database(":memory:")
    u1 = User.create("u1", "User One", "one@example.com", "111", "222")
    u2 = User.create("u2", "User Two", "two@example.com", "333", "444")

    db.save_user(u1)
    db.save_user(u2)

    fetched = db.get_user("u1")
    assert fetched is not None
    assert fetched.user_id == "u1"
    # PII fields retrieved from DB are still ciphertext
    assert fetched.pii_fields["email"].startswith("gAAAAA")

    all_users = db.list_users()
    assert len(all_users) == 2
    assert {u.user_id for u in all_users} == {"u1", "u2"}
