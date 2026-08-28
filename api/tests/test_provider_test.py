"""Hermetic tests for POST /api/providers/test/{name} — no real subprocess/network."""
import json
import subprocess

import pytest

import api.services.provider_test as pt


def _fake_run(monkeypatch, stdout: str):
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")
    calls = []
    kw_calls = []

    def run(*a, **k):
        calls.append(a[0])
        kw_calls.append(k)
        return fake

    monkeypatch.setattr("api.services.provider_test.subprocess.run", run)
    return calls, kw_calls


def test_unknown_provider_no_subprocess(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "api.services.provider_test.subprocess.run",
        lambda *a, **k: calls.append(a),
    )
    r = client.post("/api/providers/test/not_a_provider", json={"config": {"api_key": "x"}})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert "Unknown provider" in body["message"]
    assert body["latency_ms"] == 0
    assert calls == [], "unknown provider must not shell out"


def test_success_path(client, monkeypatch):
    calls, kw_calls = _fake_run(monkeypatch, '{"ok": true, "error": null}')
    r = client.post("/api/providers/test/openai", json={"config": {"api_key": "sk-test-123"}})
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "openai"
    assert body["success"] is True
    assert "Connected" in body["message"]
    assert isinstance(body["latency_ms"], int)
    assert body["latency_ms"] >= 0
    # probe received only the relevant trimmed keys, never extra config
    assert len(calls) == 1
    probe_config = json.loads(calls[0][3])
    assert probe_config == {"api_key": "sk-test-123"}
    # subprocess runs with UTF-8 forced so non-ASCII provider errors never mask the real one
    assert kw_calls[0]["env"]["PYTHONIOENCODING"] == "utf-8"
    assert kw_calls[0]["env"]["PYTHONUTF8"] == "1"
    assert kw_calls[0]["env"]["PATH"] != "", "inherits parent env"
    # api_key must never leak into the HTTP response
    assert "sk-test-123" not in json.dumps(body)


def test_failure_path(client, monkeypatch):
    _fake_run(monkeypatch, '{"ok": false, "error": "401 Unauthorized: bad key"}')
    r = client.post("/api/providers/test/openai", json={"config": {"api_key": "sk-bad"}})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert "401" in body["message"]


def test_timeout_expired(client, monkeypatch):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd=a[0], timeout=k.get("timeout"))

    monkeypatch.setattr("api.services.provider_test.subprocess.run", boom)
    r = client.post("/api/providers/test/openai", json={"config": {"api_key": "x"}})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert "timed out" in body["message"]


def test_masked_key_short_circuits(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "api.services.provider_test.subprocess.run",
        lambda *a, **k: calls.append(a[0]),
    )
    r = client.post(
        "/api/providers/test/openrouter",
        json={"config": {"api_key": "sk-••••here"}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False
    assert "API key" in body["message"]
    assert calls == [], "masked key must not shell out to the probe"


def test_masked_body_falls_back_to_disk_key(client, monkeypatch, tmp_path):
    # Test-first flow: a masked literal from GET /config must NOT be tested —
    # the real saved key on disk is used instead.
    disk = tmp_path / "cfg.yaml"
    disk.write_text("ai_providers:\n  openai:\n    api_key: sk-disk-real-999\n")
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", disk)
    calls, _ = _fake_run(monkeypatch, '{"ok": true, "error": null}')
    r = client.post(
        "/api/providers/test/openai",
        json={"config": {"api_key": "sk-••••here"}},
    )
    assert r.status_code == 200
    assert r.json()["success"] is True
    probe_cfg = json.loads(calls[0][3])
    assert probe_cfg.get("api_key") == "sk-disk-real-999"


def test_raises_without_body(client, monkeypatch):
    # no request body at all → falls back to on-disk config (empty in tests)
    _fake_run(monkeypatch, '{"ok": false, "error": "empty"}')
    r = client.post("/api/providers/test/openai")
    assert r.status_code == 200
    assert r.json()["success"] is False