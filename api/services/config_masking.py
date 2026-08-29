"""Masking + merge helpers extracted from config_service.

Centralises secret handling so config_service Overall Code Complexity
(file-level sum) drops. Re-exported via config_service for compat.
"""

from __future__ import annotations

from collections.abc import Callable

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


def _mask_webhook(v: str) -> str:
    return "••••" + v[-8:] if len(v) >= 8 else "••••"


def _identity(v: object) -> object:
    return v


def _safe_masker(fn: Callable[[str], str]) -> Callable[[object], object]:
    def _wrapped(v: object) -> object:
        return fn(v) if isinstance(v, str) and v else v  # type: ignore[arg-type]

    return _wrapped


_MASKERS: dict[str, Callable[[object], object]] = {
    "api_key": _safe_masker(_mask_api_key),
    "nvd_api_key": _safe_masker(lambda v: "••••"),
    "github_token": _safe_masker(lambda v: "••••"),
    "webhook_url": _safe_masker(_mask_webhook),
    "from_address": _safe_masker(lambda v: "••••"),
    "password": _safe_masker(lambda v: "••••"),
    "hibp_api_key": _safe_masker(lambda v: "••••"),
}


def _masked_nested(v: object, k: str) -> object:
    return mask_config(v) if isinstance(v, dict) else _MASKERS.get(k, _identity)(v)  # type: ignore[arg-type,operator]


def mask_config(data: dict) -> dict:
    return {k: _masked_nested(v, k) for k, v in data.items()}
