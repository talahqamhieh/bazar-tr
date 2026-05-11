import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "catalog.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def search_books_by_topic(topic):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title FROM books WHERE topic = ? ORDER BY id",
            (topic,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_book_by_id(item_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, topic, price, quantity FROM books WHERE id = ?",
            (item_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_book_by_id(item_id, price=None, quantity=None):
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM books WHERE id = ?",
            (item_id,),
        ).fetchone()
        if existing is None:
            return None

        updates = []
        params = []
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)

        params.append(item_id)
        conn.execute(
            f"UPDATE books SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        conn.commit()

        row = conn.execute(
            "SELECT id, title, topic, price, quantity FROM books WHERE id = ?",
            (item_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()
