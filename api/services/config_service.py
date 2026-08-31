from pathlib import Path

import yaml

from ..database import CONFIG_PATH
from .config_masking import _SECRET_KEYS as _SECRET_KEYS  # noqa: PLC0414 - re-export
from .config_masking import (
    _is_masked_value as _is_masked_value,  # noqa: PLC0414 - re-export
)
from .config_masking import (
    _merge_preserve_masked as _merge_preserve_masked,  # noqa: PLC0414 - re-export
)
from .config_masking import mask_config as mask_config  # noqa: PLC0414 - re-export


def read_config(path: Path | None = None) -> dict:
    if path is None:
        path = CONFIG_PATH
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def write_config(data: dict, path: Path | None = None) -> None:
    if path is None:
        path = CONFIG_PATH
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


_KEYLESS_PROVIDERS = {"ollama", "lmstudio"}


def get_provider_status() -> list[dict]:
    config = read_config()
    providers = config.get("ai_providers", {})
    statuses = []
    for name, cfg in providers.items():
        if name in _KEYLESS_PROVIDERS:
            has_key = bool(cfg.get("enabled")) and bool(
                str(cfg.get("base_url") or "").strip()
            )
        else:
            has_key = bool(str(cfg.get("api_key") or "").strip())
        statuses.append(
            {
                "name": name,
                "enabled": cfg.get("enabled", False),
                "configured": has_key,
                "model": cfg.get("model", ""),
                "base_url": cfg.get("base_url", ""),
            }
        )
    return statuses


def update_provider(name: str, fields: dict) -> None:
    config = read_config()
    if "ai_providers" not in config:
        config["ai_providers"] = {}
    if name not in config["ai_providers"]:
        config["ai_providers"][name] = {}
    config["ai_providers"][name].update(fields)
    write_config(config)
