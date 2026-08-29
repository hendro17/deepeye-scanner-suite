"""Shared test helpers — subprocess fakes + probe request deduped for CodeScene."""

from __future__ import annotations

import json
import subprocess
from typing import Any


def _build_fake_process(
    stdout: str, returncode: int = 0
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=""
    )


def make_fake_run(monkeypatch: Any, stdout: str) -> subprocess.CompletedProcess[str]:
    """Install fake subprocess.run returning CompletedProcess with stdout."""
    fake = _build_fake_process(stdout)
    monkeypatch.setattr(
        "api.services.provider_test.subprocess.run", lambda *a, **k: fake
    )
    return fake


def make_fake_run_with_capture(
    monkeypatch: Any, stdout: str
) -> tuple[list[Any], list[dict[str, Any]]]:
    """Install fake subprocess.run and capture calls/kwargs. Returns (calls, kw_calls)."""
    fake = _build_fake_process(stdout)
    calls: list[Any] = []
    kw_calls: list[dict[str, Any]] = []

    def _run(*a: Any, **k: Any) -> subprocess.CompletedProcess[str]:
        calls.append(a[0] if a else None)
        kw_calls.append(k)
        return fake

    monkeypatch.setattr("api.services.provider_test.subprocess.run", _run)
    return calls, kw_calls


# --- shared probe request helpers (dedupe CodeScene) ---


def probe_post(client: Any, provider: str, config: dict[str, Any] | None) -> Any:
    """Single place for POST /api/providers/test/{provider}."""
    url = f"/api/providers/test/{provider}"
    if config is None:
        return client.post(url)
    return client.post(url, json={"config": config})


def run_probe_case(
    client: Any,
    monkeypatch: Any,
    stdout: str,
    provider: str = "openai",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fake subprocess output then POST probe. Returns response json body."""
    make_fake_run(monkeypatch, stdout)
    return probe_post(client, provider, config).json()


def run_probe_case_with_capture(
    client: Any,
    monkeypatch: Any,
    stdout: str,
    provider: str = "openai",
    config: dict[str, Any] | None = None,
) -> tuple[Any, list[Any], list[dict[str, Any]]]:
    """Fake with capture then POST. Returns (response, calls, kw_calls)."""
    calls, kw_calls = make_fake_run_with_capture(monkeypatch, stdout)
    resp = probe_post(client, provider, config)
    return resp, calls, kw_calls


def assert_probe_failed(body: dict[str, Any], substr: str | None = None) -> None:
    assert body["success"] is False
    if substr is not None:
        assert substr in body["message"]


def assert_probe_succeeded(body: dict[str, Any]) -> None:
    assert body["success"] is True
    assert "Connected" in body["message"]


def assert_no_leak(body: dict[str, Any], secret: str) -> None:
    assert secret not in json.dumps(body)
