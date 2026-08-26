def _insert_finding(conn, job_id: int, finding: dict):
    conn.execute(
        "INSERT INTO findings (job_id, type, severity, url, parameter, fingerprint) VALUES (?, ?, ?, ?, ?, ?)",
        (
            job_id,
            finding.get("type"),
            finding.get("severity"),
            finding.get("url"),
            finding.get("parameter"),
            finding.get("fingerprint"),
        ),
    )


def test_compare_scans(client):
    a = client.post("/api/scans", json={"target_url": "http://example.com"}).json()["id"]
    b = client.post("/api/scans", json={"target_url": "http://example.com"}).json()["id"]

    from api.database import get_db
    conn = get_db()
    _insert_finding(conn, a, {"type": "sqli", "severity": "high", "url": "http://example.com/a", "parameter": "id", "fingerprint": "fp-a"})
    _insert_finding(conn, a, {"type": "xss", "severity": "low", "url": "http://example.com/r"})
    _insert_finding(conn, b, {"type": "sqli", "severity": "critical", "url": "http://example.com/a", "parameter": "id", "fingerprint": "fp-a"})
    _insert_finding(conn, b, {"type": "ssti", "severity": "high", "url": "http://example.com/b", "parameter": "tpl"})
    conn.commit()
    conn.close()

    r = client.post("/api/scans/compare", json={"scan_id_a": a, "scan_id_b": b})
    assert r.status_code == 200
    body = r.json()

    assert body["new_count"] == 1
    assert body["new_vulnerabilities"][0]["type"] == "ssti"
    assert body["resolved_count"] == 1
    assert body["resolved_vulnerabilities"][0]["type"] == "xss"
    assert body["persisting_count"] == 1
    assert body["severity_changes"] == [{
        "type": "sqli",
        "url": "http://example.com/a",
        "parameter": "id",
        "severity_a": "high",
        "severity_b": "critical",
    }]
    assert body["scan_a"]["id"] == a
    assert body["scan_b"]["id"] == b


def test_compare_scans_not_found(client):
    r = client.post("/api/scans/compare", json={"scan_id_a": 9999, "scan_id_b": 8888})
    assert r.status_code == 404
