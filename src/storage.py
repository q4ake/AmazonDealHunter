import os
import sqlite3
from datetime import datetime, timezone


class PriceStorage:
    def __init__(self, database_path: str):
        self.database_path = database_path
        os.makedirs(os.path.dirname(database_path) or ".", exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    store TEXT NOT NULL,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            """)
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_price_lookup "
                "ON price_history (asin, store, id)"
            )

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def add_price(self, product: dict):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT price FROM price_history "
                "WHERE asin = ? AND store = ? ORDER BY id DESC LIMIT 1",
                (product["asin"], product["store"]),
            ).fetchone()

            previous_price = float(row[0]) if row else None
            connection.execute(
                """INSERT INTO price_history
                (asin, store, title, price, currency, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    product["asin"], product["store"], product["title"],
                    float(product["price"]), product["currency"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

        return previous_price
