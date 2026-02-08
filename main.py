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

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

console = Console()



def main():
    initialize_db()

    if not vault_initialized():
        setup_master_password()

    try:
        key = login()
        show_banner()
    except Exception as e:
        print(str(e))
        return

    while True:
        show_menu()
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
                console.print("[yellow]No entries found.[/yellow]")
            else:
                show_entries_table(entries, key)

        elif choice == "3":
            entries = fetch_all_entries()

            if not entries:
                warning("No entries available.")
                continue

            show_entries_table(entries, key)

            try:
                selection = int(input("Select entry number to view: ")) - 1
                entry_id = entries[selection][0]
            except (ValueError, IndexError):
                error("Invalid selection.")
                continue

            entry = fetch_entry_by_id(entry_id)
            if not entry:
                error("Entry not found.")
                continue

            service_enc, user_enc, pass_enc, notes_enc = entry

            service = decrypt_field(service_enc, key)
            username = decrypt_field(user_enc, key)
            password = decrypt_field(pass_enc, key)
            notes = decrypt_field(notes_enc, key) if notes_enc else ""

            show_entry(service, username, password, notes)


        
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
                print(error("Invalid selection."))
                continue

            confirm = input("Type DELETE to confirm: ")
            if confirm != "DELETE":
                print("Delete cancelled.")
                continue

            delete_entry(entry_id)
            print(success("Entry deleted."))

        elif choice == "5":
            entries = fetch_all_entries()
            if not entries:
                print(warning("No entries available."))
                continue

            for idx, (eid, service_enc, user_enc) in enumerate(entries, 1):
                service = decrypt_field(service_enc, key)
                username = decrypt_field(user_enc, key)
                print(f"{idx}. {service} ({username})")

            try:
                selection = int(input("Select entry number: ")) - 1
                entry_id = entries[selection][0]
            except (ValueError, IndexError):
                print(error("Invalid selection."))
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
            
            except ValueError as e:
                print(f"Error: {e}")
                continue

            password = generate_password(
                    length=length,
                    use_upper=use_upper,
                    use_digits=use_digits,
                    use_symbols=use_symbols
            )

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
            print(console.print("\n🔒 Vault locked. Goodbye.", style="dim"))
            break

        else:
            print(error("Invalid selection."))

def clear_clipboard_after_delay(delay: int):
    time.sleep(delay)
    pyperclip.copy("")

def generate_password(
    length=16,
    use_upper=True,
    use_digits=True,
    use_symbols=True
):
    lowercase = "abcdefghijkmnopqrstuvwxyz"  # always included
    uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ" if use_upper else ""
    digits = "23456789" if use_digits else ""
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?" if use_symbols else ""

    pool = lowercase + uppercase + digits + symbols

    if not pool:
        raise ValueError("No character sets selected.")

    return "".join(secrets.choice(pool) for _ in range(length))

def show_banner():
    banner = Text()
    banner.append("RX7Pass\n", style="bold cyan")
    banner.append("Secure CLI Password Vault 🔐", style="dim")

    console.print(
        Panel(
            Align.center(banner),
            border_style="cyan",
            padding=(1, 4)
        )
    )

def show_menu():
    menu_text = Text()
    menu_text.append("1. Add password\n", style="bold")
    menu_text.append("2. List services\n")
    menu_text.append("3. View entry\n")
    menu_text.append("4. Delete entry\n")
    menu_text.append("5. Copy password to clipboard\n")
    menu_text.append("6. Generate password\n")
    menu_text.append("7. Exit\n")

    console.print(
        Panel(
            menu_text,
            title="RX7Pass Menu",
            border_style="blue"
        )
    )

def show_entries_table(entries, key):
    table = Table(title="Stored Passwords", header_style="bold magenta")

    table.add_column("#", style="dim", width=4)
    table.add_column("Service", style="cyan")
    table.add_column("Username", style="green")

    for idx, (eid, service_enc, user_enc) in enumerate(entries, 1):
        service = decrypt_field(service_enc, key)
        username = decrypt_field(user_enc, key)
        table.add_row(str(idx), service, username)

    console.print(table)

def success(msg):
    console.print(f"✅ {msg}", style="green")

def error(msg):
    console.print(f"❌ {msg}", style="red")

def warning(msg):
    console.print(f"⚠️ {msg}", style="yellow")

def show_entry(service, username, password, notes):
    body = Text()
    body.append(f"Service: {service}\n", style="cyan")
    body.append(f"Username: {username}\n", style="green")
    body.append(f"Password: {password}\n", style="bold red")

    if notes:
        body.append("\nNotes:\n", style="bold yellow")
        body.append(notes, style="yellow")

    console.print(
        Panel(
            body,
            title="Password Entry",
            border_style="red"
        )
    )

if __name__ == "__main__":
    main()
