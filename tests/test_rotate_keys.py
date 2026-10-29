import os
import tempfile
import pytest
from cryptography.fernet import InvalidToken
from data_broker_bot.adapters.base import BaseAdapter
from data_broker_bot.config import generate_key
from data_broker_bot.db import Database
from data_broker_bot.models import User
from scripts.rotate_keys import rotate_database_keys, main as rotate_main


def test_rotate_database_keys_success():
    old_key = generate_key()
    new_key = generate_key()

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        db = Database(db_path)
        u1 = User.create("u1", "Alice", "alice@example.com", "123", "456", key=old_key)
        u2 = User.create("u2", "Bob", "bob@example.com", "789", "012", key=old_key)
        db.save_user(u1)
        db.save_user(u2)

        # Rotate keys
        count = rotate_database_keys(old_key=old_key, new_key=new_key, db_path=db_path)
        assert count == 2

        # Verify decryption with new key succeeds and old key fails
        adapter = BaseAdapter()
        u1_rotated = db.get_user("u1")

        with pytest.raises(InvalidToken):
            adapter.submit(u1_rotated, key=old_key)

        res = adapter.submit(u1_rotated, key=new_key)
        assert res["submitted_pii"]["email"] == "alice@example.com"

        u2_rotated = db.get_user("u2")
        res2 = adapter.submit(u2_rotated, key=new_key)
        assert res2["submitted_pii"]["email"] == "bob@example.com"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_rotate_keys_cli(monkeypatch, capsys):
    old_key = generate_key()
    new_key = generate_key()

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        db = Database(db_path)
        user = User.create("u1", "Charlie", "charlie@example.com", "123", "456", key=old_key)
        db.save_user(user)

        monkeypatch.setattr(
            "sys.argv",
            ["rotate_keys.py", "--old-key", old_key, "--new-key", new_key, "--db-path", db_path],
        )
        rotate_main()

        captured = capsys.readouterr()
        assert "Successfully rotated encryption keys for 1 user record(s)." in captured.out

        # Verify new key works
        adapter = BaseAdapter()
        rotated_user = db.get_user("u1")
        res = adapter.submit(rotated_user, key=new_key)
        assert res["submitted_pii"]["email"] == "charlie@example.com"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
