# storage.py

import sqlite3
import uuid
from datetime import datetime
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_meta (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                password_hash BLOB NOT NULL,
                salt BLOB NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_entries (
                id TEXT PRIMARY KEY,
                service BLOB NOT NULL,
                username BLOB NOT NULL,
                password BLOB NOT NULL,
                notes BLOB,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def fetch_master_credentials():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT password_hash, salt
            FROM vault_meta
            WHERE id = 1
        """)
        row = cursor.fetchone()

        if row is None:
            raise RuntimeError("Vault not initialized.")

        return row


def vault_initialized() -> bool:
    try:
        fetch_master_credentials()
        return True
    except RuntimeError:
        return False


def store_master_credentials(password_hash: bytes, salt: bytes):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO vault_meta (id, password_hash, salt)
            VALUES (1, ?, ?)
        """, (password_hash, salt))
        conn.commit()


def insert_entry(service, username, password, notes):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO password_entries
            (id, service, username, password, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            service,
            username,
            password,
            notes,
            datetime.utcnow().isoformat()
        ))
        conn.commit()


def fetch_all_entries():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, service, username
            FROM password_entries
        """)
        return cursor.fetchall()

def fetch_entry_by_id(entry_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT service, username, password, notes
            FROM password_entries
            WHERE id = ?
        """, (entry_id,))
        return cursor.fetchone()

def delete_entry(entry_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM password_entries
            WHERE id = ?
        """, (entry_id,))
        conn.commit()

