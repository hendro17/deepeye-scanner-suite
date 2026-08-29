"""Cover provider probe branches: OSError, invalid JSON, scanner_python fallback."""

import json
import sys

import api.services.provider_test as pt
from api.services import provider_probe
from api.tests.helpers import (
    ProbeCase,
    assert_probe_failed,
    install_fake_provider,
    probe_post,
    run_probe_case,
)


def test_provider_probe_invalid_json(client, monkeypatch):
    body = run_probe_case(
        client,
        ProbeCase(
            stdout="not json {", provider="openai", config={"api_key": "sk-valid-123"}
        ),
        monkeypatch,
    )
    assert_probe_failed(body, "Invalid probe")


def test_provider_probe_oserror(client, monkeypatch):
    def boom(*a, **k):
        raise OSError("no such file")

    monkeypatch.setattr("api.services.provider_test.subprocess.run", boom)
    body = probe_post(client, "openai", {"api_key": "sk-valid"}).json()
    assert body["success"] is False
    assert "no such file" in body["message"]


def test_provider_probe_empty_error_field(client, monkeypatch):
    body = run_probe_case(
        client,
        ProbeCase(
            stdout='{"ok": false, "error": null}',
            provider="openai",
            config={"api_key": "sk-ok"},
        ),
        monkeypatch,
    )
    assert_probe_failed(body, "Probe failed")


def test_provider_probe_missing_error_key(client, monkeypatch):
    body = run_probe_case(
        client,
        ProbeCase(stdout='{"ok": false}', provider="grok", config={"api_key": "sk-ok"}),
        monkeypatch,
    )
    assert_probe_failed(body)


def test_scanner_python_fallback_no_venv(monkeypatch, tmp_path):
    fake_scanner = tmp_path / "scanner"
    fake_scanner.mkdir()
    monkeypatch.setattr("api.services.provider_test.SCANNER_DIR", fake_scanner)
    # PYTHON empty to hit sys.executable branch (line 62)
    monkeypatch.setattr("api.services.provider_test.PYTHON", "")
    # ensure no .venv candidate exists
    assert pt._scanner_python() == sys.executable
    # with PYTHON set, returns PYTHON
    monkeypatch.setattr("api.services.provider_test.PYTHON", "/usr/bin/python3")
    assert pt._scanner_python() == "/usr/bin/python3"
    # with candidate exists, returns candidate
    venv_py = fake_scanner / ".venv" / "bin" / "python"
    venv_py.parent.mkdir(parents=True, exist_ok=True)
    venv_py.write_text("#")
    assert pt._scanner_python() == str(venv_py)


def test_provider_probe_script_missing_args(capsys):
    orig_argv = sys.argv
    sys.argv = ["provider_probe.py"]
    provider_probe.main()
    out = capsys.readouterr().out
    assert json.loads(out)["ok"] is False
    assert "missing args" in json.loads(out)["error"]
    sys.argv = orig_argv


def test_provider_probe_script_bad_config(capsys):
    sys.argv = ["provider_probe.py", "openai", "not-json"]
    provider_probe.main()
    out = capsys.readouterr().out
    assert json.loads(out)["error"] == "bad config"


def test_provider_probe_script_unknown_provider(capsys):
    sys.argv = ["provider_probe.py", "unknown_xyz", json.dumps({"api_key": "x"})]
    provider_probe.main()
    out = capsys.readouterr().out
    assert "unknown provider" in json.loads(out)["error"].lower()


def test_provider_probe_script_success(monkeypatch, capsys):
    install_fake_provider()
    sys.argv = ["provider_probe.py", "openai", json.dumps({"api_key": "sk-123"})]
    provider_probe.main()
    out = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(out)["ok"] is True
    sys.modules.pop("ai_providers.openai_provider", None)


def test_provider_probe_script_empty_response_is_ok(monkeypatch, capsys):
    def _raise_empty(*_a, **_k):
        raise RuntimeError("empty response from model")

    install_fake_provider(_raise_empty)
    sys.argv = ["provider_probe.py", "openai", json.dumps({"api_key": "sk-123"})]
    provider_probe.main()
    out = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(out)["ok"] is True
    sys.modules.pop("ai_providers.openai_provider", None)


def test_provider_probe_script_exception_is_failure(monkeypatch, capsys):
    def _raise_401(*_a, **_k):
        raise RuntimeError("401 bad key")

    install_fake_provider(_raise_401)
    sys.argv = ["provider_probe.py", "openai", json.dumps({"api_key": "sk-bad"})]
    provider_probe.main()
    out = capsys.readouterr().out.strip().splitlines()[-1]
    j = json.loads(out)
    assert j["ok"] is False and "401" in j["error"]
    sys.modules.pop("ai_providers.openai_provider", None)


def test_prepare_config_overlay_ignored_masked(monkeypatch, tmp_path):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("ai_providers:\n  openai:\n    api_key: sk-real\n    model: gpt-4\n")
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", cfg)
    base, _ = pt._prepare_config("openai", {"api_key": "sk-••••", "model": "gpt-3"})
    # masked api_key ignored, model applied
    assert base["api_key"] == "sk-real"
    assert base["model"] == "gpt-3"
