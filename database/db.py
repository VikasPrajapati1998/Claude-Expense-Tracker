import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash


def get_db():
    db = sqlite3.connect(current_app.config.get("DATABASE", "spendly.db"))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.commit()
    db.close()


def seed_db():
    db = get_db()
    existing = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        db.close()
        return

    password_hash = generate_password_hash("demo123")
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    expenses = [
        (user_id, 45.50,  "Food",          "2026-06-01", "Groceries"),
        (user_id, 12.00,  "Transport",     "2026-06-02", "Bus pass"),
        (user_id, 120.00, "Bills",         "2026-06-03", "Electricity bill"),
        (user_id, 30.00,  "Health",        "2026-06-04", "Pharmacy"),
        (user_id, 25.00,  "Entertainment", "2026-06-05", "Netflix"),
        (user_id, 80.00,  "Shopping",      "2026-06-05", "Clothing"),
        (user_id, 15.00,  "Other",         "2026-06-05", "Miscellaneous"),
        (user_id, 22.50,  "Food",          "2026-06-05", "Restaurant dinner"),
    ]
    db.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    db.commit()
    db.close()
