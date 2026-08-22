import pytest


@pytest.fixture
def db(monkeypatch, tmp_path):
    monkeypatch.setattr("api.database.DATA_DIR", tmp_path)
    monkeypatch.setattr("api.database.DB_PATH", tmp_path / "test.db")
    from api.database import init_db
    init_db()
    return tmp_path / "test.db"


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)
