import time
import threading
import pyperclip
import secrets

from storage import (
    initialize_db,
    vault_initialized,
    insert_entry,
    fetch_all_entries,
    fetch_entry_by_id,
    delete_entry
)
from auth import setup_master_password, login
from crypto import encrypt_field, decrypt_field


def main():
    initialize_db()

    if not vault_initialized():
        setup_master_password()

    try:
        key = login()
    except Exception as e:
        print(str(e))
        return

    while True:
        print("\nRX7Pass Menu")
        print("1. Add password")
        print("2. List services")
        print("3. View entry")
        print("4. Delete Entry")
        print("5. Copy password to clipboard")
        print("6. Generate password")
        print("7. Exit")

        choice = input("Select: ").strip()

        if choice == "1":
            service = input("Service: ")
            username = input("Username: ")
            password = input("Password: ")
            notes = input("Notes (optional): ")

            insert_entry(
                encrypt_field(service, key),
                encrypt_field(username, key),
                encrypt_field(password, key),
                encrypt_field(notes, key) if notes else None
            )

            print("Entry added securely.")

        elif choice == "2":
            entries = fetch_all_entries()
            if not entries:
                print("No entries found.")
                continue

            for idx, (eid, service_enc, user_enc) in enumerate(entries, 1):
                service = decrypt_field(service_enc, key)
                username = decrypt_field(user_enc, key)
                print(f"{idx}. {service} ({username})")

        elif choice == "3":
            entries = fetch_all_entries()
            if not entries:
                print("No entries available.")
                continue

            for idx, (eid, service_enc, user_enc) in enumerate(entries, 1):
                service = decrypt_field(service_enc, key)
                username = decrypt_field(user_enc, key)
                print(f"{idx}. {service} ({username})")

            try:
                selection = int(input("Select entry number: ")) - 1
                entry_id = entries[selection][0]
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            entry = fetch_entry_by_id(entry_id)
            if not entry:
                print("Entry not found.")
                continue

            service, username, password, notes = entry

            print("\nService:", decrypt_field(service, key))
            print("Username:", decrypt_field(username, key))
            print("Password: ********")

            reveal = input("Reveal password? (y/N): ").lower()
            if reveal == "y":
                print("Password:", decrypt_field(password, key))

            if notes:
                print("Notes:", decrypt_field(notes, key))
        
        elif choice == "4":
            entries = fetch_all_entries()
            if not entries:
                print("No entries to delete.")
                continue

            for idx, (eid, service_enc, user_enc) in enumerate(entries, 1):
                service = decrypt_field(service_enc, key)
                username = decrypt_field(user_enc, key)
                print(f"{idx}. {service} ({username})")

            try:
                selection = int(input("Select entry number to delete: ")) - 1
                entry_id = entries[selection][0]
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            confirm = input("Type DELETE to confirm: ")
            if confirm != "DELETE":
                print("Delete cancelled.")
                continue

            delete_entry(entry_id)
            print("Entry deleted.")

        elif choice == "5":
            entries = fetch_all_entries()
            if not entries:
                print("No entries available.")
                continue

            for idx, (eid, service_enc, user_enc) in enumerate(entries, 1):
                service = decrypt_field(service_enc, key)
                username = decrypt_field(user_enc, key)
                print(f"{idx}. {service} ({username})")

            try:
                selection = int(input("Select entry number: ")) - 1
                entry_id = entries[selection][0]
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            entry = fetch_entry_by_id(entry_id)
            if not entry:
                print("Entry not found.")
                continue

            _, _, password_enc, _ = entry
            password = decrypt_field(password_enc, key)

            pyperclip.copy(password)
            print("Password copied to clipboard. Will clear in 15 seconds.")

            threading.Thread(
                target=clear_clipboard_after_delay,
                args=(15,),
                daemon=True
            ).start()

        elif choice == "6":
            try:
                length_input = input("Length (default 16): ").strip()
                length = int(length_input) if length_input else 16

                if length < 8 or length > 64:
                    print("Length must be between 8 and 64.")
                    continue

                use_symbols = input("Include symbols? (y/n): ").lower() == "y"
                use_digits = input("Include numbers? (y/n): ").lower() == "y"
                use_upper = input("Include uppercase? (y/n): ").lower() == "y"

                password = generate_password(
                    length=length,
                    use_upper=use_upper,
                    use_digits=use_digits,
                    use_symbols=use_symbols
                )

            except ValueError as e:
                print(f"Error: {e}")
                continue

            pyperclip.copy(password)
            print("Password copied to clipboard.")

            show = input("Show password once? (y/n): ").lower()
            if show == "y":
                print(password)

            threading.Thread(
                target=clear_clipboard_after_delay,
                args=(15,),
                daemon=True
            ).start()

        elif choice == "7":
            print("Vault locked.")
            break

        else:
            print("Invalid option.")

def clear_clipboard_after_delay(delay: int):
    time.sleep(delay)
    pyperclip.copy("")

def generate_password(
    length=16,
    use_upper=True,
    use_digits=True,
    use_symbols=True
):
    lowercase = "abcdefghijkmnopqrstuvwxyz"  # removed l
    uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ" if use_upper else ""
    digits = "23456789" if use_digits else ""
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?" if use_symbols else ""

    pool = lowercase + uppercase + digits + symbols

    if not pool:
        raise ValueError("No character sets selected.")

    return "".join(secrets.choice(pool) for _ in range(length))

if __name__ == "__main__":
    main()
