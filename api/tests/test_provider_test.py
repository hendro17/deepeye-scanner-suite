"""Hermetic tests for POST /api/providers/test/{name} — no real subprocess/network."""

import json
import subprocess

from api.tests.helpers import (
    assert_no_leak,
    assert_probe_failed,
    assert_probe_succeeded,
    probe_post,
    run_probe_case,
    run_probe_case_with_capture,
)


def test_unknown_provider_no_subprocess(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "api.services.provider_test.subprocess.run",
        lambda *a, **k: calls.append(a),
    )
    r = probe_post(client, "not_a_provider", {"api_key": "x"})
    assert r.status_code == 200
    body = r.json()
    assert_probe_failed(body, "Unknown provider")
    assert body["latency_ms"] == 0
    assert calls == [], "unknown provider must not shell out"


def test_success_path(client, monkeypatch):
    resp, calls, kw_calls = run_probe_case_with_capture(
        client,
        monkeypatch,
        '{"ok": true, "error": null}',
        provider="openai",
        config={"api_key": "sk-test-123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "openai"
    assert_probe_succeeded(body)
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
    assert_no_leak(body, "sk-test-123")


def test_failure_path(client, monkeypatch):
    body = run_probe_case(
        client,
        monkeypatch,
        '{"ok": false, "error": "401 Unauthorized: bad key"}',
        provider="openai",
        config={"api_key": "sk-bad"},
    )
    # response still 200 — probe failure is in body.success
    assert_probe_failed(body, "401")


def test_timeout_expired(client, monkeypatch):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd=a[0], timeout=k.get("timeout"))

    monkeypatch.setattr("api.services.provider_test.subprocess.run", boom)
    r = probe_post(client, "openai", {"api_key": "x"})
    assert r.status_code == 200
    body = r.json()
    assert_probe_failed(body, "timed out")


def test_masked_key_short_circuits(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "api.services.provider_test.subprocess.run",
        lambda *a, **k: calls.append(a[0]),
    )
    r = probe_post(client, "openrouter", {"api_key": "sk-••••here"})
    assert r.status_code == 200
    body = r.json()
    assert_probe_failed(body, "API key")
    assert calls == [], "masked key must not shell out to the probe"


def test_masked_body_falls_back_to_disk_key(client, monkeypatch, tmp_path):
    # Test-first flow: a masked literal from GET /config must NOT be tested —
    # the real saved key on disk is used instead.
    disk = tmp_path / "cfg.yaml"
    disk.write_text("ai_providers:\n  openai:\n    api_key: sk-disk-real-999\n")
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", disk)
    resp, calls, _ = run_probe_case_with_capture(
        client,
        monkeypatch,
        '{"ok": true, "error": null}',
        provider="openai",
        config={"api_key": "sk-••••here"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    probe_cfg = json.loads(calls[0][3])
    assert probe_cfg.get("api_key") == "sk-disk-real-999"


def test_raises_without_body(client, monkeypatch):
    # no request body at all → falls back to on-disk config (empty in tests)
    resp, _, _ = run_probe_case_with_capture(
        client,
        monkeypatch,
        '{"ok": false, "error": "empty"}',
        provider="openai",
        config=None,
    )
    assert resp.status_code == 200
    assert_probe_failed(resp.json())
