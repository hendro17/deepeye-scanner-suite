import json

YAML_SPEC = """\
openapi: 3.0.0
info:
  title: Demo
servers:
  - url: https://api.example.com/v1/
paths:
  /users:
    get: {}
  /users/{id}:
    get: {}
"""


def _args_json(client, job_id):
    from api.database import get_db

    conn = get_db()
    row = conn.execute("SELECT args_json FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    return json.loads(row["args_json"])


def test_create_scan_accepts_recon_mode_and_secrets_fields(client):
    r = client.post(
        "/api/scans",
        json={
            "target_url": "http://example.com",
            "enable_recon": True,
            "full_scan": True,
            "quick_scan": False,
            "scan_subdomains": True,
            "secrets_enabled": True,
            "secret_patterns": ["aws_access_key", "github_token"],
        },
    )
    assert r.status_code == 200
    args = _args_json(client, r.json()["id"])
    assert args["enable_recon"] is True
    assert args["full_scan"] is True
    assert args["quick_scan"] is False
    assert args["scan_subdomains"] is True
    assert args["secrets_enabled"] is True
    assert args["secret_patterns"] == ["aws_access_key", "github_token"]


def test_build_cmd_maps_no_fake_flags_for_unsupported_fields():
    from api.services.engine_runner import build_cmd

    cmd = build_cmd(
        {
            "target_url": "http://example.com",
            "formats": ["html"],
            "scope_nl": "only /api/*",
            "enable_recon": True,
            "full_scan": True,
            "quick_scan": True,
            "scan_subdomains": True,
            "secrets_enabled": True,
            "secret_patterns": ["aws_access_key"],
        }
    )
    assert "--scope-nl" in cmd and "--formats" in cmd
    assert not any(
        "recon" in part
        or "subdomain" in part
        or "secret" in part
        or part in ("--full-scan", "--quick-scan")
        for part in cmd
    )


def test_ingest_openapi_yaml_v3(client):
    r = client.post(
        "/api/scans/ingest-openapi",
        json={"filename": "spec.yaml", "content": YAML_SPEC},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 2
    assert body["targets"] == [
        "https://api.example.com/v1/users",
        "https://api.example.com/v1/users/{id}",
    ]


def test_ingest_openapi_json_swagger2(client):
    spec = json.dumps(
        {
            "swagger": "2.0",
            "host": "api.example.com",
            "basePath": "/v2/",
            "schemes": ["https"],
            "paths": {"/pets": {"get": {}}, "/stores": {"get": {}}},
        }
    )
    r = client.post(
        "/api/scans/ingest-openapi", json={"filename": "spec.json", "content": spec}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["targets"] == [
        "https://api.example.com/v2/pets",
        "https://api.example.com/v2/stores",
    ]
    assert body["count"] == 2


def test_ingest_openapi_skips_relative_servers_and_dedupes(client):
    spec = json.dumps(
        {
            "openapi": "3.0.0",
            "servers": [
                {"url": "https://a.example.com"},
                {"url": "/relative-only"},
                {"url": "https://a.example.com/"},
            ],
            "paths": {"/x": {}, "/y": {}},
        }
    )
    r = client.post(
        "/api/scans/ingest-openapi", json={"filename": "spec.yaml", "content": spec}
    )
    assert r.status_code == 200
    assert r.json()["targets"] == ["https://a.example.com/x", "https://a.example.com/y"]


def test_ingest_openapi_invalid_content(client):
    r = client.post(
        "/api/scans/ingest-openapi", json={"filename": "bad.yaml", "content": "\t: : ["}
    )
    assert r.status_code == 400


def test_ingest_openapi_non_object_spec(client):
    r = client.post(
        "/api/scans/ingest-openapi", json={"filename": "list.json", "content": "[1, 2]"}
    )
    assert r.status_code == 400
