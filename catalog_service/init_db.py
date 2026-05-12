import sqlite3

from config import DB_PATH

BOOKS = [
    (1, "How to get a good grade in DOS in 40 minutes a day", "distributed systems", 40, 8),
    (2, "RPCs for Noobs", "distributed systems", 50, 5),
    (3, "Xen and the Art of Surviving Undergraduate School", "undergraduate school", 35, 7),
    (4, "Cooking for the Impatient Undergrad", "undergraduate school", 25, 6),
    # Lab 2 placeholder values until the lab specifies exact catalog fields.
    (5, "How to finish Project 3 on time", "distributed systems", 45, 4),
    (6, "Why theory classes are so hard", "undergraduate school", 30, 5),
    (7, "Spring in the Pioneer Valley", "undergraduate school", 20, 4),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL
            )
            """
        )
        conn.execute("DELETE FROM books")
        conn.executemany(
            "INSERT INTO books (id, title, topic, price, quantity) VALUES (?, ?, ?, ?, ?)",
            BOOKS,
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Catalog database initialized at {DB_PATH}")
