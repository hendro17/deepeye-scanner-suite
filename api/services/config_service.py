import yaml
from pathlib import Path

from ..database import CONFIG_PATH


def read_config(path: Path | None = None) -> dict:
    if path is None:
        path = CONFIG_PATH
    with open(path) as f:
        return yaml.safe_load(f) or {}


def write_config(data: dict, path: Path | None = None) -> None:
    if path is None:
        path = CONFIG_PATH
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def mask_config(data: dict) -> dict:
    masked = {}
    for key, val in data.items():
        if isinstance(val, dict):
            masked[key] = mask_config(val)
        elif key == "api_key" and isinstance(val, str) and val:
            masked[key] = val[:3] + "••••" + val[-4:] if len(val) > 7 else "••••"
        elif key in ("nvd_api_key", "github_token") and isinstance(val, str) and val:
            masked[key] = "••••"
        elif key in ("webhook_url",) and isinstance(val, str) and val:
            masked[key] = "••••" + val[-8:]
        elif key in ("from_address",) and isinstance(val, str) and val:
            masked[key] = "••••"
        else:
            masked[key] = val
    return masked


def get_provider_status() -> list[dict]:
    config = read_config()
    providers = config.get("ai_providers", {})
    statuses = []
    for name, cfg in providers.items():
        has_key = bool(cfg.get("api_key")) if name != "ollama" else bool(cfg.get("base_url"))
        statuses.append({
            "name": name,
            "enabled": cfg.get("enabled", False),
            "configured": has_key,
            "model": cfg.get("model", ""),
            "base_url": cfg.get("base_url", ""),
        })
    return statuses


def update_provider(name: str, fields: dict) -> None:
    config = read_config()
    if "ai_providers" not in config:
        config["ai_providers"] = {}
    if name not in config["ai_providers"]:
        config["ai_providers"][name] = {}
    config["ai_providers"][name].update(fields)
    write_config(config)
