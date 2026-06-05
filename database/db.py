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
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL
        );
    """)
    db.commit()
    db.close()


def seed_db():
    pass
