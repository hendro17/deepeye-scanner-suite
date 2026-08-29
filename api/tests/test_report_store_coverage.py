import json

from api.database import get_db
from api.services.report_store import get_findings, list_reports, parse_findings


def test_parse_findings_list_data(db, tmp_path, monkeypatch):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'completed')",
        ("http://list.com", "{}"),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    # data as list fallback
    lst = [{"type": "XSS", "severity": "low", "url": "http://x"}, {"type": "SQLi"}]
    report = tmp_path / "r.json"
    report.write_text(json.dumps(lst))
    cnt = parse_findings(job_id, report)
    assert cnt == 2
    conn = get_db()
    rows = conn.execute("SELECT * FROM findings WHERE job_id=?", (job_id,)).fetchall()
    conn.close()
    assert len(rows) == 2


def test_list_reports_filters_and_missing(monkeypatch, tmp_path, db):
    import api.database as dbmod
    import api.services.report_store as rs

    # nonexistent
    monkeypatch.setattr(dbmod, "REPORTS_DIR", tmp_path / "nonexistent")
    monkeypatch.setattr(rs, "REPORTS_DIR", tmp_path / "nonexistent")
    assert list_reports() == []
    # existent with mixed files
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    # create files with different ext
    (reports_dir / "a.html").write_text("html")
    (reports_dir / "b.json").write_text("{}")
    (reports_dir / "c.txt").write_text("ignore")
    (reports_dir / "d.pdf").write_text("pdf")
    (reports_dir / "e.sarif").write_text("sarif")
    monkeypatch.setattr(dbmod, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(rs, "REPORTS_DIR", reports_dir)
    files = list_reports()
    filenames = {f["filename"] for f in files}
    assert "a.html" in filenames
    assert "b.json" in filenames
    assert "d.pdf" in filenames
    assert "c.txt" not in filenames
    # check fields
    for f in files:
        assert "size" in f and "created_at" in f and "format" in f


def test_get_findings_with_report_path_success(monkeypatch, tmp_path, db):
    import api.database as dbmod
    import api.services.report_store as rs

    reports_dir = tmp_path / "reports2"
    reports_dir.mkdir()
    monkeypatch.setattr(dbmod, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(rs, "REPORTS_DIR", reports_dir)
    # create json report with urls_crawled/duration
    report_file = reports_dir / "rep.json"
    report_file.write_text(
        json.dumps({"urls_crawled": 42, "duration": 123, "vulnerabilities": []})
    )
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status, report_path) VALUES (?, ?, 'completed', ?)",
        ("http://t.com", "{}", str(report_file)),
    )
    job_id = cur.lastrowid
    conn.execute(
        "INSERT INTO findings (job_id, severity) VALUES (?, ?)", (job_id, "high")
    )
    conn.execute(
        "INSERT INTO findings (job_id, severity) VALUES (?, ?)", (job_id, "high")
    )
    conn.execute(
        "INSERT INTO findings (job_id, severity) VALUES (?, ?)", (job_id, "low")
    )
    conn.commit()
    conn.close()
    res = get_findings(job_id)
    assert res["urls_crawled"] == 42
    assert res["duration"] == 123
    assert res["total"] == 3
    assert res["severity_counts"]["high"] == 2
    assert res["target"] == "http://t.com"


def test_get_findings_with_invalid_json_report(monkeypatch, tmp_path, db):
    import api.database as dbmod
    import api.services.report_store as rs

    reports_dir = tmp_path / "rep3"
    reports_dir.mkdir()
    monkeypatch.setattr(dbmod, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(rs, "REPORTS_DIR", reports_dir)
    bad_file = reports_dir / "bad.json"
    bad_file.write_text("not json {")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status, report_path) VALUES (?, ?, 'completed', ?)",
        ("http://t2.com", "{}", str(bad_file)),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    res = get_findings(job_id)
    assert res["urls_crawled"] == 0
    assert res["duration"] is None


def test_get_findings_no_job(monkeypatch, tmp_path, db):
    # job not found
    res = get_findings(99999)
    assert res["total"] == 0
    assert res["vulnerabilities"] == []
    assert res["target"] is None


def test_get_findings_report_path_non_json(monkeypatch, tmp_path, db):
    import api.database as dbmod
    import api.services.report_store as rs

    reports_dir = tmp_path / "rep4"
    reports_dir.mkdir()
    monkeypatch.setattr(dbmod, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(rs, "REPORTS_DIR", reports_dir)
    html_file = reports_dir / "rep.html"
    html_file.write_text("<html></html>")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status, report_path) VALUES (?, ?, 'completed', ?)",
        ("http://t3.com", "{}", str(html_file)),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    res = get_findings(job_id)
    assert res["urls_crawled"] == 0


def test_get_findings_report_path_missing_file(db):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status, report_path) VALUES (?, ?, 'completed', ?)",
        ("http://t4.com", "{}", "/nonexistent/path.json"),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    res = get_findings(job_id)
    assert res["urls_crawled"] == 0


def test_parse_findings_with_cve_none_and_false_positive(db, tmp_path):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'completed')",
        ("http://x.com", "{}"),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    report = tmp_path / "r2.json"
    report.write_text(
        json.dumps(
            {
                "vulnerabilities": [
                    {"type": "XSS", "cve_references": None, "false_positive": None}
                ]
            }
        )
    )
    cnt = parse_findings(job_id, report)
    assert cnt == 1
