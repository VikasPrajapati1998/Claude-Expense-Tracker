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


# ── seed_db() ─────────────────────────────────────────────────────────────────

def test_seed_db_inserts_demo_user(app_ctx):
    init_db()
    seed_db()
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()
    assert user is not None
    assert user["name"] == "Demo User"
    db.close()


def test_seed_db_hashes_password(app_ctx):
    from werkzeug.security import check_password_hash
    init_db()
    seed_db()
    db = get_db()
    user = db.execute(
        "SELECT password_hash FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()
    assert check_password_hash(user["password_hash"], "demo123")
    db.close()


def test_seed_db_inserts_eight_expenses(app_ctx):
    init_db()
    seed_db()
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    assert count == 8
    db.close()


def test_seed_db_no_duplicates_on_repeat(app_ctx):
    init_db()
    seed_db()
    seed_db()   # second call must skip
    db = get_db()
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    expense_count = db.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    assert user_count == 1
    assert expense_count == 8
    db.close()


def test_seed_db_covers_all_categories(app_ctx):
    init_db()
    seed_db()
    db = get_db()
    categories = {
        row["category"]
        for row in db.execute("SELECT DISTINCT category FROM expenses").fetchall()
    }
    expected = {"Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"}
    assert expected.issubset(categories)
    db.close()
