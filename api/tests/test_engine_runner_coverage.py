import asyncio
import json
import queue
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from api.services import engine_runner


def test_build_cmd_variants():
    job = {"target_url": "http://example.com"}
    cmd = engine_runner.build_cmd(job)
    assert "-u" in cmd and "http://example.com" in cmd
    assert "--no-banner" in cmd
    # with formats
    job2 = {"target_url": "http://x.com", "formats": ["html", "json"]}
    cmd2 = engine_runner.build_cmd(job2)
    assert "--formats" in cmd2
    assert "html,json" in cmd2
    # with scope_nl
    job3 = {"target_url": "http://x.com", "scope_nl": "only example"}
    cmd3 = engine_runner.build_cmd(job3)
    assert "--scope-nl" in cmd3
    assert "only example" in cmd3


def test_finalize_scan_no_reports_dir(monkeypatch, tmp_path):
    import api.database as dbmod

    nonexist = tmp_path / "nope"
    monkeypatch.setattr(dbmod, "REPORTS_DIR", nonexist)
    monkeypatch.setattr(engine_runner, "REPORTS_DIR", nonexist)
    # need db
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", db_path)
    dbmod.init_db()
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t.com", "{}"),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    result = engine_runner._finalize_scan(job_id, 0, set())
    assert result is None
    conn = dbmod.get_db()
    row = conn.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
    assert row["status"] == "completed"
    conn.close()
    # failed
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t.com", "{}"),
    )
    job_id2 = cur.lastrowid
    conn.commit()
    conn.close()
    engine_runner._finalize_scan(job_id2, 1, set())
    conn = dbmod.get_db()
    row = conn.execute("SELECT status FROM jobs WHERE id=?", (job_id2,)).fetchone()
    assert row["status"] == "failed"
    conn.close()


def test_finalize_scan_with_new_json(monkeypatch, tmp_path):
    import api.database as dbmod

    reports = tmp_path / "reports"
    reports.mkdir()
    # create before files
    (reports / "old.json").write_text("{}")
    before = {"old.json"}
    # new file after
    (reports / "new.json").write_text(
        json.dumps({"vulnerabilities": [{"type": "XSS"}]})
    )
    (reports / "new.sarif.json").write_text("{}")  # should be ignored
    monkeypatch.setattr(dbmod, "REPORTS_DIR", reports)
    monkeypatch.setattr(engine_runner, "REPORTS_DIR", reports)
    # also need to patch report_store.REPORTS_DIR
    monkeypatch.setattr("api.services.report_store.REPORTS_DIR", reports)
    db_path = tmp_path / "test2.db"
    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", db_path)
    dbmod.init_db()
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t.com", "{}"),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    # patch parse_findings to verify called
    with patch("api.services.report_store.parse_findings") as mock_parse:
        mock_parse.return_value = 1
        result = engine_runner._finalize_scan(job_id, 0, before)
        assert result is not None
        assert "new.json" in result
        mock_parse.assert_called_once()
    # no json new files
    (reports / "new2.html").write_text("html")
    before2 = {"old.json", "new.json", "new.sarif.json"}
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t2.com", "{}"),
    )
    job_id2 = cur.lastrowid
    conn.commit()
    conn.close()
    with patch("api.services.report_store.parse_findings") as mock_parse2:
        result2 = engine_runner._finalize_scan(job_id2, 0, before2)
        # new html not json, so no report_path
        assert result2 is None
        mock_parse2.assert_not_called()


def test_start_scan_mocks(monkeypatch, tmp_path):
    import time

    import api.database as dbmod

    reports = tmp_path / "reports_start"
    reports.mkdir()
    (reports / "existing.json").write_text("{}")
    monkeypatch.setattr(dbmod, "REPORTS_DIR", reports)
    monkeypatch.setattr(engine_runner, "REPORTS_DIR", reports)
    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "db_start.db")
    dbmod.init_db()
    mock_proc = MagicMock()
    mock_proc.pid = 12345
    mock_proc.stdout = ["\x1b[31mhello\x1b[0m\n", "world\n"]
    mock_proc.wait = MagicMock()
    mock_proc.returncode = 0
    with (
        patch("subprocess.Popen", return_value=mock_proc) as mock_popen,
        patch.object(engine_runner, "_finalize_scan", return_value="/tmp/fake.json"),
    ):
        pid = engine_runner.start_scan(
            1, {"target_url": "http://example.com", "formats": ["html"]}
        )
        assert pid == 12345
        assert 1 in engine_runner.active_scans
        # allow reader thread to process
        time.sleep(0.15)
        q = engine_runner.active_scans[1]["queue"]
        # should have at least log entries + done
        items = []
        while not q.empty():
            items.append(q.get_nowait())
        assert any(i[0] == "log" for i in items)
        assert any(i[0] == "done" for i in items)
        # clean ansi: first log should be stripped
        logs = [i[1] for i in items if i[0] == "log"]
        assert "hello" in logs[0]
        assert "\x1b" not in logs[0]
        engine_runner.active_scans.pop(1, None)
        mock_popen.assert_called_once()


def test_start_scan_no_reports_dir(monkeypatch, tmp_path):
    import time

    import api.database as dbmod

    nonexist = tmp_path / "no_reports"
    monkeypatch.setattr(dbmod, "REPORTS_DIR", nonexist)
    monkeypatch.setattr(engine_runner, "REPORTS_DIR", nonexist)
    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "db2.db")
    dbmod.init_db()
    mock_proc = MagicMock()
    mock_proc.pid = 999
    mock_proc.stdout = []
    mock_proc.wait = MagicMock()
    mock_proc.returncode = 1
    with (
        patch("subprocess.Popen", return_value=mock_proc),
        patch.object(engine_runner, "_finalize_scan", return_value=None),
    ):
        pid = engine_runner.start_scan(2, {"target_url": "http://example.com"})
        assert pid == 999
        time.sleep(0.1)
        assert 2 in engine_runner.active_scans
        engine_runner.active_scans.pop(2, None)


def test_stop_scan_branches(monkeypatch, tmp_path):
    import api.database as dbmod

    monkeypatch.setattr(dbmod, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "stop.db")
    dbmod.init_db()
    # not found
    assert engine_runner.stop_scan(9999) is False
    # with missing process
    engine_runner.active_scans[10] = {"process": None, "done": False}
    assert engine_runner.stop_scan(10) is False
    engine_runner.active_scans.pop(10, None)
    # successful terminate
    mock_proc = MagicMock()
    mock_proc.terminate = MagicMock()
    mock_proc.wait = MagicMock()
    mock_proc.kill = MagicMock()
    engine_runner.active_scans[11] = {"process": mock_proc, "done": False}
    # need job in db
    conn = dbmod.get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://t.com", "{}"),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    # map scan id 11 to actual job? stop_scan uses job_id as key for db update
    # we set active_scans key as job_id same as db id for test
    engine_runner.active_scans.pop(11, None)
    engine_runner.active_scans[job_id] = {"process": mock_proc, "done": False}
    result = engine_runner.stop_scan(job_id)
    assert result is True
    assert engine_runner.active_scans[job_id]["done"] is True
    mock_proc.terminate.assert_called_once()
    engine_runner.active_scans.pop(job_id, None)
    # TimeoutExpired branch
    mock_proc2 = MagicMock()
    mock_proc2.terminate = MagicMock()
    mock_proc2.wait = MagicMock(
        side_effect=subprocess.TimeoutExpired(cmd="x", timeout=5)
    )
    mock_proc2.kill = MagicMock()
    engine_runner.active_scans[20] = {"process": mock_proc2, "done": False}
    # need job id 20 not necessarily in db but stop_scan will still try to update db
    # create job 20
    conn = dbmod.get_db()
    conn.execute(
        "INSERT INTO jobs (id, target, args_json, status) VALUES (?, ?, ?, ?)",
        (20, "http://t.com", "{}", "pending"),
    )
    conn.commit()
    conn.close()
    res = engine_runner.stop_scan(20)
    assert res is True
    mock_proc2.kill.assert_called_once()
    engine_runner.active_scans.pop(20, None)
    # ProcessLookupError
    mock_proc3 = MagicMock()
    mock_proc3.terminate = MagicMock(side_effect=ProcessLookupError)
    engine_runner.active_scans[30] = {"process": mock_proc3, "done": False}
    conn = dbmod.get_db()
    conn.execute(
        "INSERT OR IGNORE INTO jobs (id, target, args_json, status) VALUES (?, ?, ?, ?)",
        (30, "http://t.com", "{}", "pending"),
    )
    conn.commit()
    conn.close()
    res3 = engine_runner.stop_scan(30)
    assert res3 is True
    engine_runner.active_scans.pop(30, None)


@pytest.mark.asyncio
async def test_stream_scan_not_found():
    gen = engine_runner.stream_scan(99999)
    chunks = []
    async for chunk in gen:
        chunks.append(chunk)
        break
    assert any("Scan not found" in c for c in chunks)


@pytest.mark.asyncio
async def test_stream_scan_success(monkeypatch):
    q = queue.Queue()
    q.put(("log", "hello", "2024-01-01T00:00:00Z"))
    q.put(("done", "/path/report.json", 0))
    engine_runner.active_scans[42] = {"queue": q, "done": False, "process": MagicMock()}

    # mock asyncio.to_thread to return queue items directly
    async def fake_to_thread(func, *args, **kwargs):
        return q.get_nowait()

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    gen = engine_runner.stream_scan(42)
    outputs = []
    async for chunk in gen:
        outputs.append(chunk)
        if len(outputs) >= 2:
            break
    assert any("log" in o for o in outputs)
    assert any("done" in o for o in outputs)
    engine_runner.active_scans.pop(42, None)


@pytest.mark.asyncio
async def test_stream_scan_keepalive_and_done(monkeypatch):
    # queue empty then done flag
    q = queue.Queue()
    engine_runner.active_scans[43] = {"queue": q, "done": True, "process": MagicMock()}

    async def fake_to_thread_raise(func, *args, **kwargs):
        raise queue.Empty

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread_raise)
    gen = engine_runner.stream_scan(43)
    # should break immediately because done True after Empty
    chunks = []
    async for chunk in gen:
        chunks.append(chunk)
    # either keepalive or break
    assert len(chunks) == 0 or any("keepalive" in c for c in chunks)
    engine_runner.active_scans.pop(43, None)
    # now test keepalive path when not done
    q2 = queue.Queue()
    engine_runner.active_scans[44] = {
        "queue": q2,
        "done": False,
        "process": MagicMock(),
    }
    call_count = {"c": 0}

    async def fake_to_thread_keepalive(func, *args, **kwargs):
        call_count["c"] += 1
        if call_count["c"] == 1:
            raise queue.Empty
        # second call return done
        return ("done", None, 0)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread_keepalive)
    gen2 = engine_runner.stream_scan(44)
    outputs2 = []
    async for chunk in gen2:
        outputs2.append(chunk)
        if len(outputs2) >= 2:
            break
    assert any("keepalive" in o for o in outputs2) or any("done" in o for o in outputs2)
    engine_runner.active_scans.pop(44, None)
