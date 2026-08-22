import json

from api.database import get_db
from api.services.report_store import parse_findings


def test_parse_findings_full(db, tmp_path):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'completed')",
        ("http://example.com", "{}"),
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()

    mock_report = {
        "target": "http://example.com",
        "vulnerabilities": [
            {
                "type": "XSS",
                "severity": "high",
                "url": "http://example.com/search?q=test",
                "parameter": "q",
                "payload": "<script>alert(1)</script>",
                "evidence": "Reflected input detected",
                "remediation": "Encode output",
                "description": "Reflected XSS in search parameter",
                "screenshot": "base64data==",
                "fingerprint": "abc123",
                "cve_references": ["CVE-2024-1234"],
                "ai_evidence_summary": "Confirmed XSS vulnerability",
                "false_positive": False,
            },
            {
                "type": "SQLi",
                "severity": "critical",
                "url": "http://example.com/login",
                "parameter": "username",
                "payload": "' OR 1=1--",
                "evidence": "Database error in response",
                "remediation": "Use parameterized queries",
            },
        ],
        "severity_summary": {"critical": 1, "high": 1},
    }
    report_file = tmp_path / "deep_eye_example.com_20260820_143000.json"
    report_file.write_text(json.dumps(mock_report))

    count = parse_findings(job_id, report_file)
    assert count == 2

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM findings WHERE job_id=? ORDER BY id", (job_id,)
    ).fetchall()
    conn.close()

    assert len(rows) == 2
    xss = rows[0]
    assert xss["type"] == "XSS"
    assert xss["severity"] == "high"
    assert xss["description"] == "Reflected XSS in search parameter"
    assert xss["screenshot"] == "base64data=="
    assert xss["fingerprint"] == "abc123"

    sqli = rows[1]
    assert sqli["type"] == "SQLi"
    assert sqli["severity"] == "critical"
    assert sqli["description"] is None
    assert sqli["screenshot"] is None


def test_parse_findings_empty(db, tmp_path):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'completed')",
        ("http://safe.com", "{}"),
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()

    report_file = tmp_path / "deep_eye_safe.com_20260820.json"
    report_file.write_text(json.dumps({"vulnerabilities": []}))

    count = parse_findings(job_id, report_file)
    assert count == 0
