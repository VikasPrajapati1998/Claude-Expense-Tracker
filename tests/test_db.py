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


# ── init_db() ─────────────────────────────────────────────────────────────────

def test_init_db_creates_users_table(app_ctx):
    init_db()
    db = get_db()
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone()
    assert row is not None
    db.close()


def test_init_db_creates_expenses_table(app_ctx):
    init_db()
    db = get_db()
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'"
    ).fetchone()
    assert row is not None
    db.close()


def test_init_db_is_idempotent(app_ctx):
    init_db()
    init_db()   # second call must not raise or insert data
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 0
    db.close()
