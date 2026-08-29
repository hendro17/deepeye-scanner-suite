import sqlite3


def test_init_db_adds_missing_columns(monkeypatch, tmp_path):
    import api.database as dbmod

    # create old DB without description/screenshot
    db_path = tmp_path / "old.db"
    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", db_path)
    # manually create findings table without those columns
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT NOT NULL, args_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT (datetime('now')));
        CREATE TABLE findings (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL, type TEXT, severity TEXT, url TEXT);
    """)
    conn.close()
    # now init_db should add missing columns
    dbmod.init_db()
    conn = dbmod.get_db()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(findings)").fetchall()}
    assert "description" in cols
    assert "screenshot" in cols
    conn.close()


def test_main_startup(monkeypatch, tmp_path):
    import api.database as dbmod

    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "startup.db")
    from fastapi.testclient import TestClient

    from api.main import app

    # TestClient will trigger startup event
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
