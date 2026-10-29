import argparse
import os
import sys
from typing import Optional
from data_broker_bot.crypto import decrypt_pii, encrypt_pii
from data_broker_bot.db import Database


def rotate_database_keys(
    old_key: str,
    new_key: str,
    db_path: str = ":memory:",
    db: Optional[Database] = None,
) -> int:
    """Rotate Fernet encryption keys for all user PII fields in the database."""
    target_db = db or Database(db_path)
    users = target_db.list_users()
    rotated_count = 0

    for user in users:
        # Decrypt PII fields using old_key
        decrypted_pii = decrypt_pii(user.pii_fields, key=old_key)
        # Re-encrypt PII fields using new_key
        reencrypted_pii = encrypt_pii(decrypted_pii, key=new_key)
        # Update record in DB
        target_db.update_user_pii(user.user_id, reencrypted_pii)
        rotated_count += 1

    return rotated_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Rotate PII encryption key for stored database records.")
    parser.add_argument("--old-key", help="Current PII encryption key")
    parser.add_argument("--new-key", help="New PII encryption key")
    parser.add_argument("--db-path", default="bot.db", help="Path to SQLite database file")

    args = parser.parse_args()

    old_key = args.old_key or os.environ.get("OLD_PII_ENCRYPTION_KEY") or os.environ.get("PII_ENCRYPTION_KEY")
    new_key = args.new_key or os.environ.get("NEW_PII_ENCRYPTION_KEY")

    if not old_key:
        print("Error: --old-key or OLD_PII_ENCRYPTION_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not new_key:
        print("Error: --new-key or NEW_PII_ENCRYPTION_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    count = rotate_database_keys(old_key=old_key, new_key=new_key, db_path=args.db_path)
    print(f"Successfully rotated encryption keys for {count} user record(s).")


if __name__ == "__main__":
    main()
