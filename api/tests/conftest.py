import pytest


@pytest.fixture
def db(monkeypatch, tmp_path):
    monkeypatch.setattr("api.database.DATA_DIR", tmp_path)
    monkeypatch.setattr("api.database.DB_PATH", tmp_path / "test.db")
    # isolate config file so CI without submodule still passes and writes are sandboxed
    fake_cfg = tmp_path / "config.yaml"
    fake_cfg.write_text("ai_providers: {}\n")
    monkeypatch.setattr("api.database.CONFIG_PATH", fake_cfg)
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", fake_cfg, raising=False)
    from api.database import init_db
    init_db()
    return tmp_path / "test.db"


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)
