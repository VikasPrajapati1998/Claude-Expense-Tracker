# Database Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `get_db()`, `init_db()`, and `seed_db()` in `database/db.py` and wire them into `app.py` startup, establishing the SQLite data layer for Spendly.

**Architecture:** `database/db.py` is a standalone module with three functions — `get_db()` opens a connection, `init_db()` creates tables idempotently, and `seed_db()` inserts demo data exactly once. `app.py` imports all three and calls `init_db()` + `seed_db()` inside an `app_context` at startup. DB path is read from `current_app.config["DATABASE"]` (defaulting to `"spendly.db"`) so tests can inject a temp path without hitting the real file.

**Tech Stack:** Python 3.10+, Flask 3.1, SQLite3 (stdlib), werkzeug.security, pytest, pytest-flask

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `database/db.py` | Modify (replace stub) | All three DB helpers |
| `app.py` | Modify | Import helpers, call on startup |
| `tests/conftest.py` | Create | pytest fixtures with temp DB |
| `tests/test_db.py` | Create | Tests for all three functions + constraints |

> Also save a copy of this plan to `.claude/plans/01-database-setup.md` at the start of execution.

---

## Task 1: Create `tests/conftest.py`

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Create the conftest with a temp-DB fixture**

```python
import os
import pytest
from app import app as flask_app


@pytest.fixture
def app(tmp_path):
    db_path = str(tmp_path / "test_spendly.db")
    flask_app.config["DATABASE"] = db_path
    flask_app.config["TESTING"] = True
    yield flask_app
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield


@pytest.fixture
def client(app):
    with app.app_context():
        from database.db import init_db, seed_db
        init_db()
        seed_db()
    return app.test_client()
```

- [ ] **Step 2: Verify conftest is importable (no syntax errors)**

```bash
pytest --collect-only
```

Expected: `no tests ran` or collection with 0 items — no import errors.

---

## Task 2: Write failing tests for `get_db()`

**Files:**
- Create: `tests/test_db.py`

- [ ] **Step 1: Write the failing tests**

```python
import pytest
import sqlite3
from database.db import get_db, init_db, seed_db


# ── get_db() ──────────────────────────────────────────────────────────────────

def test_get_db_returns_connection(app_ctx):
    db = get_db()
    assert db is not None
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
    assert result[0] == 1
    db.close()
```

- [ ] **Step 2: Run and confirm they fail**

```bash
pytest tests/test_db.py::test_get_db_returns_connection tests/test_db.py::test_get_db_uses_row_factory tests/test_db.py::test_get_db_foreign_keys_on -v
```

Expected: `ImportError` or `ModuleNotFoundError` for `get_db` — confirms stub is empty.

---

## Task 3: Implement `get_db()`

**Files:**
- Modify: `database/db.py`

- [ ] **Step 1: Replace the stub with the full module header and `get_db()`**

```python
import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash


def get_db():
    db = sqlite3.connect(current_app.config.get("DATABASE", "spendly.db"))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db
```

- [ ] **Step 2: Run `get_db()` tests and confirm they pass**

```bash
pytest tests/test_db.py::test_get_db_returns_connection tests/test_db.py::test_get_db_uses_row_factory tests/test_db.py::test_get_db_foreign_keys_on -v
```

Expected: 3 PASSED.

- [ ] **Step 3: Commit**

```bash
git add database/db.py tests/conftest.py tests/test_db.py
git commit -m "feat: implement get_db() with row_factory and FK enforcement"
```

---

## Task 4: Write and pass tests for `init_db()`

**Files:**
- Modify: `tests/test_db.py` (append)

- [ ] **Step 1: Append `init_db()` tests to `tests/test_db.py`**

```python
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
```

- [ ] **Step 2: Run and confirm they fail**

```bash
pytest tests/test_db.py::test_init_db_creates_users_table tests/test_db.py::test_init_db_creates_expenses_table tests/test_db.py::test_init_db_is_idempotent -v
```

Expected: FAIL — `init_db` not defined yet.

- [ ] **Step 3: Implement `init_db()` in `database/db.py`**

Append after `get_db()`:

```python
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
```

- [ ] **Step 4: Run `init_db()` tests and confirm they pass**

```bash
pytest tests/test_db.py::test_init_db_creates_users_table tests/test_db.py::test_init_db_creates_expenses_table tests/test_db.py::test_init_db_is_idempotent -v
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add database/db.py tests/test_db.py
git commit -m "feat: implement init_db() with users and expenses schema"
```

---

## Task 5: Write and pass tests for `seed_db()`

**Files:**
- Modify: `tests/test_db.py` (append)

- [ ] **Step 1: Append `seed_db()` tests**

```python
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
```

- [ ] **Step 2: Run and confirm they fail**

```bash
pytest tests/test_db.py -k "seed" -v
```

Expected: FAIL — `seed_db` not defined yet.

- [ ] **Step 3: Implement `seed_db()` in `database/db.py`**

Append after `init_db()`:

```python
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
```

- [ ] **Step 4: Run all `seed_db()` tests and confirm they pass**

```bash
pytest tests/test_db.py -k "seed" -v
```

Expected: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add database/db.py tests/test_db.py
git commit -m "feat: implement seed_db() with demo user and 8 sample expenses"
```

---

## Task 6: Write and pass constraint tests

**Files:**
- Modify: `tests/test_db.py` (append)

- [ ] **Step 1: Append constraint tests**

```python
# ── Constraint enforcement ────────────────────────────────────────────────────

def test_duplicate_email_raises_integrity_error(app_ctx):
    init_db()
    db = get_db()
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("A", "dup@test.com", "hash"),
    )
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("B", "dup@test.com", "hash"),
        )
        db.commit()
    db.close()


def test_invalid_user_id_raises_integrity_error(app_ctx):
    init_db()
    db = get_db()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (9999, 10.0, "Food", "2026-06-01"),
        )
        db.commit()
    db.close()
```

- [ ] **Step 2: Run constraint tests and confirm they pass**

```bash
pytest tests/test_db.py::test_duplicate_email_raises_integrity_error tests/test_db.py::test_invalid_user_id_raises_integrity_error -v
```

Expected: 2 PASSED.

- [ ] **Step 3: Run the full test suite to confirm nothing is broken**

```bash
pytest tests/test_db.py -v
```

Expected: All 13 tests PASSED.

- [ ] **Step 4: Commit**

```bash
git add tests/test_db.py
git commit -m "test: add constraint tests for unique email and FK enforcement"
```

---

## Task 7: Wire `init_db()` and `seed_db()` into `app.py`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add the import at the top of `app.py`**

After `from flask import Flask, render_template`, add:

```python
from database.db import get_db, init_db, seed_db
```

- [ ] **Step 2: Add startup call in the `if __name__ == "__main__"` block**

Replace the existing bottom of `app.py`:

```python
if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
```

- [ ] **Step 3: Run the app and confirm it starts without errors**

```bash
python app.py
```

Expected output includes:
```
 * Running on http://127.0.0.1:5001
```

No traceback. `spendly.db` appears in the project root.

- [ ] **Step 4: Confirm DB file was created with correct data**

```bash
python -c "
import sqlite3
db = sqlite3.connect('spendly.db')
print('users:', db.execute('SELECT COUNT(*) FROM users').fetchone()[0])
print('expenses:', db.execute('SELECT COUNT(*) FROM expenses').fetchone()[0])
db.close()
"
```

Expected:
```
users: 1
expenses: 8
```

- [ ] **Step 5: Run the full test suite one final time**

```bash
pytest tests/test_db.py -v
```

Expected: 13 PASSED, 0 failed.

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat: wire init_db and seed_db into app startup"
```

---

## Task 8: Save plan copy and push

- [ ] **Step 1: Save plan copy to project location**

```bash
# Copy plan to the project-local plans directory
mkdir -p .claude/plans
cp "C:\Users\DELL\.claude\plans\read-claude-specs-01-database-setup-md-a-resilient-quill.md" .claude/plans/01-database-setup.md
```

- [ ] **Step 2: Commit plan file**

```bash
git add .claude/plans/01-database-setup.md
git commit -m "docs: save database setup implementation plan"
```

- [ ] **Step 3: Push branch**

```bash
git push -u origin feature/database-setup
```

---

## Verification Checklist (Definition of Done)

Run these checks before declaring the task complete:

```bash
# 1. All tests pass
pytest tests/test_db.py -v

# 2. App starts without errors
python app.py &
sleep 2 && curl -s http://127.0.0.1:5001/ | head -5
pkill -f "python app.py"

# 3. DB file exists with correct row counts
python -c "
import sqlite3
db = sqlite3.connect('spendly.db')
u = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
e = db.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
cats = {r[0] for r in db.execute('SELECT DISTINCT category FROM expenses').fetchall()}
print(f'users={u}, expenses={e}, categories={len(cats)}')
assert u == 1
assert e == 8
assert len(cats) == 7
print('All checks passed.')
db.close()
"
```

Expected final output:
```
users=1, expenses=8, categories=7
All checks passed.
```
