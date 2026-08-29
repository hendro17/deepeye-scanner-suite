"""Cover provider probe branches: OSError, invalid JSON, scanner_python fallback."""

import json
import sys

import api.services.provider_test as pt
from api.services import provider_probe
from api.tests.helpers import make_fake_run as _fake_run


def test_provider_probe_invalid_json(client, monkeypatch):
    # proc returns non-JSON -> _INVALID_PROBE_MSG
    _fake_run(monkeypatch, "not json {")
    r = client.post(
        "/api/providers/test/openai", json={"config": {"api_key": "sk-valid-123"}}
    )
    body = r.json()
    assert body["success"] is False
    assert "Invalid probe" in body["message"]


def test_provider_probe_oserror(client, monkeypatch):
    def boom(*a, **k):
        raise OSError("no such file")

    monkeypatch.setattr("api.services.provider_test.subprocess.run", boom)
    r = client.post(
        "/api/providers/test/openai", json={"config": {"api_key": "sk-valid"}}
    )
    assert r.json()["success"] is False
    assert "no such file" in r.json()["message"]


def test_provider_probe_empty_error_field(client, monkeypatch):
    # {"ok": false, "error": null} -> fallback to "Probe failed"
    _fake_run(monkeypatch, '{"ok": false, "error": null}')
    r = client.post("/api/providers/test/openai", json={"config": {"api_key": "sk-ok"}})
    assert r.json()["success"] is False
    assert "Probe failed" in r.json()["message"]


def test_provider_probe_missing_error_key(client, monkeypatch):
    _fake_run(monkeypatch, '{"ok": false}')
    r = client.post("/api/providers/test/grok", json={"config": {"api_key": "sk-ok"}})
    assert r.json()["success"] is False


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
    # mock import to avoid needing real ai_providers
    import types

    mod = types.ModuleType("ai_providers.openai_provider")

    class FakeProv:
        def __init__(self, cfg):
            pass

        def generate(self, prompt, max_tokens=64):
            return "hello"

    mod.OpenAIProvider = FakeProv
    sys.modules["ai_providers.openai_provider"] = mod
    # ensure scanner in path doesn't break
    sys.argv = ["provider_probe.py", "openai", json.dumps({"api_key": "sk-123"})]
    provider_probe.main()
    out = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(out)["ok"] is True
    sys.modules.pop("ai_providers.openai_provider", None)


def test_provider_probe_script_empty_response_is_ok(monkeypatch, capsys):
    import types

    mod = types.ModuleType("ai_providers.openai_provider")

    class FakeProv:
        def __init__(self, cfg):
            pass

        def generate(self, *a, **k):
            raise RuntimeError("empty response from model")

    mod.OpenAIProvider = FakeProv
    sys.modules["ai_providers.openai_provider"] = mod
    sys.argv = ["provider_probe.py", "openai", json.dumps({"api_key": "sk-123"})]
    provider_probe.main()
    out = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(out)["ok"] is True
    sys.modules.pop("ai_providers.openai_provider", None)


def test_provider_probe_script_exception_is_failure(monkeypatch, capsys):
    import types

    mod = types.ModuleType("ai_providers.openai_provider")

    class FakeProv:
        def __init__(self, cfg):
            pass

        def generate(self, *a, **k):
            raise RuntimeError("401 bad key")

    mod.OpenAIProvider = FakeProv
    sys.modules["ai_providers.openai_provider"] = mod
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
