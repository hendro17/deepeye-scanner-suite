import yaml
from pathlib import Path
from unittest.mock import patch

def test_read_write_config(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    data = {"scanner": {"depth": 2}, "ai_providers": {"openai": {"api_key": "sk-abc12345xyz", "enabled": True}}}
    from api.services.config_service import write_config, read_config
    write_config(data, cfg_path)
    loaded = read_config(cfg_path)
    assert loaded["scanner"]["depth"] == 2
    # test empty file fallback
    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    assert read_config(empty) == {}

def test_mask_config_variants():
    from api.services.config_service import mask_config
    data = {
        "api_key": "sk-1234567890abcdef",
        "api_key_short": "abc",
        "nvd_api_key": "secret",
        "github_token": "tok",
        "webhook_url": "https://hooks.slack.com/hooks/longurl12345678",
        "from_address": "test@example.com",
        "other": "value",
        "nested": {"api_key": "sk-verylongkey1234567890", "nvd_api_key": "x", "plain": "keep"},
        "empty_key": "",
    }
    # Use actual keys checked: api_key, nvd_api_key, github_token, webhook_url, from_address
    data2 = {
        "api_key": "sk-1234567890",
        "nvd_api_key": "nvd-secret",
        "github_token": "gh-secret",
        "webhook_url": "https://example.com/webhook/abc1234567890",
        "from_address": "a@b.com",
        "nested": {"api_key": "short", "api_key2": "sk-1234567", "nvd_api_key": "nvd"},
        "normal": "keep"
    }
    masked = mask_config(data2)
    # api_key longer than 7 chars masks with prefix/suffix
    assert masked["api_key"].startswith("sk-")
    assert "••••" in masked["api_key"]
    assert masked["nvd_api_key"] == "••••"
    assert masked["github_token"] == "••••"
    assert masked["webhook_url"].endswith("4567890") or masked["webhook_url"].startswith("••••")
    assert masked["from_address"] == "••••"
    assert masked["normal"] == "keep"
    # nested api_key short
    assert masked["nested"]["api_key"] == "••••"
    # empty string should stay as empty (falsy check)
    data_empty = {"api_key": "", "nvd_api_key": ""}
    m2 = mask_config(data_empty)
    assert m2["api_key"] == ""
    assert m2["nvd_api_key"] == ""

def test_get_provider_status(monkeypatch, tmp_path):
    import api.database as db
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump({
        "ai_providers": {
            "openai": {"api_key": "sk-123", "enabled": True, "model": "gpt-4", "base_url": "https://api.openai.com"},
            "ollama": {"base_url": "http://localhost:11434", "enabled": False, "model": "llama"},
            "claude": {"enabled": True},
        }
    }))
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", cfg_path)
    monkeypatch.setattr("api.database.CONFIG_PATH", cfg_path)
    from api.services.config_service import get_provider_status
    statuses = get_provider_status()
    names = {s["name"] for s in statuses}
    assert "openai" in names
    assert "ollama" in names
    openai = next(s for s in statuses if s["name"] == "openai")
    assert openai["configured"] is True
    assert openai["model"] == "gpt-4"
    ollama = next(s for s in statuses if s["name"] == "ollama")
    assert ollama["configured"] is True
    claude = next(s for s in statuses if s["name"] == "claude")
    assert claude["configured"] is False

def test_update_provider(tmp_path, monkeypatch):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump({"ai_providers": {"openai": {"api_key": "old"}}}))
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", cfg_path)
    monkeypatch.setattr("api.database.CONFIG_PATH", cfg_path)
    from api.services.config_service import update_provider, read_config
    update_provider("openai", {"model": "gpt-4o"})
    assert read_config(cfg_path)["ai_providers"]["openai"]["model"] == "gpt-4o"
    assert read_config(cfg_path)["ai_providers"]["openai"]["api_key"] == "old"
    # new provider
    update_provider("newprov", {"api_key": "xyz"})
    assert read_config(cfg_path)["ai_providers"]["newprov"]["api_key"] == "xyz"
    # no ai_providers key
    cfg2 = tmp_path / "config2.yaml"
    cfg2.write_text(yaml.safe_dump({}))
    monkeypatch.setattr("api.services.config_service.CONFIG_PATH", cfg2)
    monkeypatch.setattr("api.database.CONFIG_PATH", cfg2)
    from importlib import reload
    # directly call again (module uses patched path at call time)
    update_provider("another", {"enabled": True})
    assert read_config(cfg2)["ai_providers"]["another"]["enabled"] is True
