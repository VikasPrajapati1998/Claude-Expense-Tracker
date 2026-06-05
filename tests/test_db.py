import pytest
import sqlite3
from database.db import get_db, init_db, seed_db


# ── get_db() ──────────────────────────────────────────────────────────────────

def test_get_db_returns_connection(app_ctx):
    db = get_db()
    result = db.execute("SELECT 1").fetchone()[0]
    assert result == 1
    db.close()


def test_get_db_uses_row_factory(app_ctx):
    init_db()
    db = get_db()
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Row", "row@test.com", "hash")
    )
    db.commit()
    row = db.execute("SELECT * FROM users WHERE email = ?", ("row@test.com",)).fetchone()
    assert row["email"] == "row@test.com"   # dict-like access via sqlite3.Row
    db.close()


def test_get_db_foreign_keys_on(app_ctx):
    db = get_db()
    result = db.execute("PRAGMA foreign_keys").fetchone()
    assert result["foreign_keys"] == 1
    db.close()
