"""Shared test helpers — subprocess fakes deduped for CodeScene health."""

from __future__ import annotations

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
