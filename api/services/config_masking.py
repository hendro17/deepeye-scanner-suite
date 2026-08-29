"""Masking + merge helpers extracted from config_service.

Centralises secret handling so config_service Overall Code Complexity
(file-level sum) drops. Re-exported via config_service for compat.
"""

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
    if not isinstance(value, str):
        return False
    s = value.strip()
    return bool(s) and ("•" in s or "…" in s or "***" in s)


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


def _mask_api_key(v: str) -> str:
    return v[:3] + "••••" + v[-4:] if len(v) > 7 else "••••"


_MASKERS: dict[str, object] = {
    "api_key": _mask_api_key,
    "nvd_api_key": lambda v: "••••",  # type: ignore[arg-type]
    "github_token": lambda v: "••••",  # type: ignore[arg-type]
    "webhook_url": lambda v: "••••" + v[-8:] if len(v) >= 8 else "••••",  # type: ignore[arg-type]
    "from_address": lambda v: "••••",  # type: ignore[arg-type]
    "password": lambda v: "••••",  # type: ignore[arg-type]
    "hibp_api_key": lambda v: "••••",  # type: ignore[arg-type]
}


def mask_config(data: dict) -> dict:
    out: dict[str, object] = {}
    for key, val in data.items():
        if isinstance(val, dict):
            out[key] = mask_config(val)
        elif key in _MASKERS and isinstance(val, str) and val:
            fn = _MASKERS[key]  # type: ignore[assignment]
            out[key] = fn(val)  # type: ignore[operator]
        else:
            out[key] = val
    return out
