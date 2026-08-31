"""Tests for api/services/engine_runner.py auth modes + provider probe port.
Covers _build_temp_config variants, chmod 0o600, cleanup.
"""

import json
import os
import stat

import pytest
import yaml

import api.database as dbmod
from api.services import engine_runner


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    # isolate DB + DATA_DIR + CONFIG_PATH + SCANNER_DIR
    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(engine_runner, "DATA_DIR", tmp_path) if hasattr(
        engine_runner, "DATA_DIR"
    ) else None
    # engine_runner imports DATA_DIR from api.database at import time, so patch both modules
    monkeypatch.setattr("api.services.engine_runner.DATA_DIR", tmp_path)
    monkeypatch.setattr("api.database.DATA_DIR", tmp_path)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.safe_dump({"scanner": {"custom_headers": {"X-Base": "1"}}}))
    monkeypatch.setattr(dbmod, "CONFIG_PATH", cfg)
    monkeypatch.setattr("api.services.engine_runner.CONFIG_PATH", cfg)
    # scanner dir tmp
    scanner = tmp_path / "scanner"
    scanner.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(dbmod, "SCANNER_DIR", scanner)
    monkeypatch.setattr("api.services.engine_runner.SCANNER_DIR", scanner)
    dbmod.init_db()
    return tmp_path, cfg, scanner


def test_build_temp_config_none_returns_config_path(isolated_db):
    _tmp_path, cfg, _ = isolated_db
    p = engine_runner._build_temp_config(1, {"auth_mode": "none"})
    assert p == cfg
    p2 = engine_runner._build_temp_config(2, {})
    assert p2 == cfg


def test_build_temp_config_cookie_headers_merges(isolated_db):
    _tmp_path, _cfg, _ = isolated_db
    job_args = {
        "auth_mode": "cookie_headers",
        "auth_headers": {"X-Custom": "abc"},
        "auth_cookies": {"sess": "123"},
    }
    p = engine_runner._build_temp_config(10, job_args)
    assert p.exists()
    # chmod 0o600
    mode = stat.S_IMODE(os.stat(p).st_mode)
    assert mode == 0o600
    data = yaml.safe_load(p.read_text())
    assert data["scanner"]["custom_headers"]["X-Base"] == "1"
    assert data["scanner"]["custom_headers"]["X-Custom"] == "abc"
    assert data["scanner"]["cookies"]["sess"] == "123"


def test_build_temp_config_cookie_headers_no_base(isolated_db):
    _tmp_path, cfg, _ = isolated_db
    cfg.write_text(yaml.safe_dump({}))  # empty base config
    job_args = {"auth_mode": "cookie_headers", "auth_headers": {"H": "v"}}
    p = engine_runner._build_temp_config(11, job_args)
    data = yaml.safe_load(p.read_text())
    assert data["scanner"]["custom_headers"]["H"] == "v"


def test_build_temp_config_form_login_creates_macro_and_chmod(isolated_db):
    tmp_path, _cfg, _ = isolated_db
    job_args = {
        "auth_mode": "form_login",
        "login_url": "http://example.com/login",
        "login_username": "admin",
        "login_password": "secret",
        "login_username_field": "user",
        "login_password_field": "pass",
        "target_url": "http://example.com/",
    }
    p = engine_runner._build_temp_config(20, job_args)
    assert p.exists()
    assert stat.S_IMODE(os.stat(p).st_mode) == 0o600
    macro = tmp_path / "tmp_scans" / "20" / "login_macro.json"
    assert macro.exists()
    assert stat.S_IMODE(os.stat(macro).st_mode) == 0o600
    data = json.loads(macro.read_text())
    assert data["steps"][0]["url"] == "http://example.com/login"
    assert any("authenticity_token" in str(s) for s in data["steps"])
    cfg_data = yaml.safe_load(p.read_text())
    assert cfg_data["login_replay"]["enabled"] is True
    assert cfg_data["login_replay"]["macro_path"] == str(macro)
    assert cfg_data["login_replay"]["_generated_for_job"] == 20


def test_build_temp_config_form_login_defaults(isolated_db):
    tmp_path, _, _ = isolated_db
    job_args = {"auth_mode": "form_login", "target_url": "http://example.com/"}
    engine_runner._build_temp_config(21, job_args)
    macro = tmp_path / "tmp_scans" / "21" / "login_macro.json"
    data = json.loads(macro.read_text())
    # defaults: username_field username, password_field password, login_url falls back to target_url
    assert data["steps"][0]["url"] == "http://example.com/"
    assert data["auth_check"]["url"] == "http://example.com/"


def test_load_base_config_missing_and_invalid(monkeypatch, tmp_path):
    missing = tmp_path / "nope.yaml"
    monkeypatch.setattr("api.services.engine_runner.CONFIG_PATH", missing)
    assert engine_runner._load_base_config() == {}
    bad = tmp_path / "bad.yaml"
    bad.write_text("::: not yaml :::\n: [")
    monkeypatch.setattr("api.services.engine_runner.CONFIG_PATH", bad)
    # yaml.safe_load will raise, _load_base_config catches and returns {}
    assert engine_runner._load_base_config() == {}
    good = tmp_path / "good.yaml"
    good.write_text(yaml.safe_dump({"a": 1}))
    monkeypatch.setattr("api.services.engine_runner.CONFIG_PATH", good)
    assert engine_runner._load_base_config() == {"a": 1}


def test_build_cmd_stores_resolved_config(isolated_db):
    _tmp_path, cfg, _scanner = isolated_db
    # none mode
    job = {"target_url": "http://example.com", "auth_mode": "none"}
    cmd = engine_runner.build_cmd(job)
    assert str(cfg) in cmd
    assert job["_resolved_config"] == str(cfg)
    # with auth
    job2 = {
        "target_url": "http://example.com",
        "auth_mode": "cookie_headers",
        "auth_headers": {"X": "1"},
        "_job_id": 99,
    }
    cmd2 = engine_runner.build_cmd(job2)
    assert "tmp_scans" in job2["_resolved_config"]
    assert "tmp_scans" in cmd2[cmd2.index("-c") + 1]


def test_finalize_scan_cleanup_removes_tmp_scans(isolated_db):
    tmp_path, _, _ = isolated_db
    # create tmp_scans/job_id dir
    job_id = 42
    td = tmp_path / "tmp_scans" / str(job_id)
    td.mkdir(parents=True, exist_ok=True)
    (td / "config.yaml").write_text("x")
    (td / "login_macro.json").write_text("{}")
    monkeypatch_reports = tmp_path / "reports"
    monkeypatch_reports.mkdir(exist_ok=True)
    # patch REPORTS_DIR for finalize
    import api.services.report_store as rs

    orig_reports = dbmod.REPORTS_DIR
    orig_er_reports = engine_runner.REPORTS_DIR
    dbmod.REPORTS_DIR = monkeypatch_reports
    engine_runner.REPORTS_DIR = monkeypatch_reports
    rs.REPORTS_DIR = monkeypatch_reports
    # create job
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t.com", "{}"),
    )
    jid = cur.lastrowid
    conn.commit()
    conn.close()
    # finalize should cleanup tmp_scans/42
    engine_runner._finalize_scan(jid, 0, set())
    # but jid !=42 so 42 still exists; now test with matching job_id
    conn = dbmod.get_db()
    conn.execute(
        "INSERT INTO jobs (id, target, args_json, status) VALUES (?, ?, ?, ?)",
        (42, "http://t.com", "{}", "pending"),
    )
    conn.commit()
    conn.close()
    engine_runner._finalize_scan(42, 0, set())
    assert not td.exists()
    # restore
    dbmod.REPORTS_DIR = orig_reports
    engine_runner.REPORTS_DIR = orig_er_reports


def test_finalize_scan_cleanup_missing_dir_no_error(isolated_db):
    _tmp_path, _, _ = isolated_db
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t.com", "{}"),
    )
    jid = cur.lastrowid
    conn.commit()
    conn.close()
    # no tmp_scans dir exists, should not raise
    engine_runner._finalize_scan(jid, 0, set())
