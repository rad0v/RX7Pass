# auth.py

import getpass
import hmac

from config import (
    MIN_MASTER_PASSWORD_LENGTH,
    SALT_SIZE,
    KDF_ITERATIONS,
    KEY_LENGTH
)
from crypto import generate_salt, derive_key
from storage import store_master_credentials, fetch_master_credentials


def setup_master_password():
    while True:
        password = getpass.getpass("Create master password: ")
        if len(password) < MIN_MASTER_PASSWORD_LENGTH:
            print(f"Password must be at least {MIN_MASTER_PASSWORD_LENGTH} characters.")
            continue

        confirm = getpass.getpass("Confirm master password: ")
        if password != confirm:
            print("Passwords do not match.")
            continue

        salt = generate_salt(SALT_SIZE)
        password_hash = derive_key(password, salt, KDF_ITERATIONS, KEY_LENGTH)

        store_master_credentials(password_hash, salt)
        print("Vault created successfully.")
        return


def login() -> bytes:
    stored_hash, salt = fetch_master_credentials()

    password = getpass.getpass("Enter master password: ")
    derived = derive_key(password, salt, KDF_ITERATIONS, KEY_LENGTH)

    if not hmac.compare_digest(derived, stored_hash):
        raise ValueError("Invalid master password.")

    print("Vault unlocked.")
    return derived
