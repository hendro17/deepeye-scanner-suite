def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_config_read(client):
    r = client.get("/api/config")
    assert r.status_code == 200
    body = r.json()
    assert "config" in body


def test_scan_create(client):
    r = client.post("/api/scans", json={
        "target_url": "http://example.com",
        "threads": 5,
        "depth": 2,
    })
    assert r.status_code == 200
    body = r.json()
    assert "id" in body
    assert body["status"] == "pending"


def test_scan_list(client):
    client.post("/api/scans", json={"target_url": "http://a.com"})
    client.post("/api/scans", json={"target_url": "http://b.com"})
    r = client.get("/api/scans")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_scan_detail(client):
    r = client.post("/api/scans", json={"target_url": "http://example.com"})
    job_id = r.json()["id"]
    r = client.get(f"/api/scans/{job_id}")
    assert r.status_code == 200
    assert r.json()["target"] == "http://example.com"


def test_scan_invalid_url(client):
    r = client.post("/api/scans", json={"target_url": "ftp://bad.com"})
    assert r.status_code == 422


def test_scan_bare_domain_normalized_to_https(client):
    r = client.post("/api/scans", json={"target_url": "example.com"})
    assert r.status_code == 200
    scan_id = r.json()["id"]
    detail = client.get(f"/api/scans/{scan_id}")
    assert detail.json()["target"] == "https://example.com"


def test_scan_formats_always_include_json(client):
    r = client.post("/api/scans", json={"target_url": "http://example.com", "formats": ["html"]})
    assert r.status_code == 200
    stored = client.get(f"/api/scans/{r.json()['id']}").json()
    assert "json" in stored["args"]["formats"]


def test_findings_empty(client):
    r = client.post("/api/scans", json={"target_url": "http://example.com"})
    job_id = r.json()["id"]
    r = client.get(f"/api/scans/{job_id}/findings")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["vulnerabilities"] == []


def test_providers_status(client):
    r = client.get("/api/providers/status")
    assert r.status_code == 200
