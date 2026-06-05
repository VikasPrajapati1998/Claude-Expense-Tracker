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
