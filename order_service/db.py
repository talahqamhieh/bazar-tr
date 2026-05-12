import sqlite3
from datetime import datetime, timezone

from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                price_at_purchase INTEGER NOT NULL,
                purchased_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def log_purchase(item_id, title, price_at_purchase):
    purchased_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO orders (item_id, title, price_at_purchase, purchased_at)
            VALUES (?, ?, ?, ?)
            """,
            (item_id, title, price_at_purchase, purchased_at),
        )
        conn.commit()
    finally:
        conn.close()


def count_successful_purchases(item_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM orders WHERE item_id = ?",
            (item_id,),
        ).fetchone()
        return row["count"]
    finally:
        conn.close()
