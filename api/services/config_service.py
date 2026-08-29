from pathlib import Path

import yaml

from ..database import CONFIG_PATH


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


_SECRET_KEYS = {
    "api_key",
    "nvd_api_key",
    "github_token",
    "webhook_url",
    "from_address",
    "password",
    "hibp_api_key",
}


def _is_masked_value(value: object) -> bool:
    """True if value looks like a masked placeholder (contains •, …, or ***)."""
    if not isinstance(value, str):
        return False
    s = value.strip()
    if not s:
        return False
    return "•" in s or "…" in s or "***" in s


def _is_nested_merge(base: dict, key: str, val: object) -> bool:
    return isinstance(val, dict) and isinstance(base.get(key), dict)


def _should_skip_masked(val: object) -> bool:
    return isinstance(val, str) and _is_masked_value(val)


def _should_preserve_empty_secret(key: str, val: object, base: dict) -> bool:
    return (
        isinstance(val, str)
        and val == ""
        and key in _SECRET_KEYS
        and bool(base.get(key))
    )


def _merge_preserve_masked(base: dict, incoming: dict) -> dict:
    """Deep-merge incoming into base, skipping masked secret values.

    Masked values (e.g. 'sk-••••e2e4') must never overwrite the real secret
    stored on disk. This mirrors the overlay logic in provider_test.py
    (_apply_overlay) but works recursively for the full config tree.
    Empty string for secret keys also preserves existing value, so frontend
    can sanitize masked placeholders to '' for UX without wiping disk.
    """
    for key, val in incoming.items():
        if _is_nested_merge(base, key, val):
            _merge_preserve_masked(base[key], val)  # type: ignore[arg-type]
            continue
        if _should_skip_masked(val):
            continue
        if _should_preserve_empty_secret(key, val, base):
            continue
        base[key] = val
    return base


def mask_config(data: dict) -> dict:
    masked: dict[str, object] = {}
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


_KEYLESS_PROVIDERS = {"ollama", "lmstudio"}


def get_provider_status() -> list[dict]:
    config = read_config()
    providers = config.get("ai_providers", {})
    statuses = []
    for name, cfg in providers.items():
        if name in _KEYLESS_PROVIDERS:
            # Keyless (ollama/lmstudio) "configured" only if enabled + base_url present.
            # Default config ships with base_url but enabled=false -> should NOT show
            # Configured badge until user actively enables. Otherwise badge toujours muncul
            # padahal user belum simpan apa pun.
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
