"""Service that tests a provider's API key by probing it in the scanner venv."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from ..database import PYTHON, SCANNER_DIR
from .config_service import read_config

PROVIDER_CLASS_MAP = {
    "openai": "OpenAIProvider",
    "claude": "ClaudeProvider",
    "grok": "GrokProvider",
    "groq": "GroqProvider",
    "gemini": "GeminiProvider",
    "mistral": "MistralProvider",
    "ollama": "OllamaProvider",
    "openrouter": "OpenRouterProvider",
    "lmstudio": "LMStudioProvider",
    "litellm": "LiteLLMProvider",
    "orcarouter": "OrcaRouterProvider",
}

PROBE_SCRIPT = Path(__file__).resolve().parent / "provider_probe.py"

_OVERLAY_KEYS = ("api_key", "base_url", "model")

_CONNECTED_MESSAGE = "Connected — provider responded"

_MASKED_HINT = (
    "No valid API key stored or entered — type the API key, click Test to verify it "
    "first, then Save to persist the change."
)

_TIMEOUT_FALLBACK = 30
_TIMEOUT_PADDING = 10
_INVALID_PROBE_MSG = "Invalid probe response"
_PROBE_FAILED_MSG = "Probe failed"


def _looks_masked_or_missing(key: object) -> bool:
    """True for masked placeholders (config GET returns masked keys, e.g. 'sk-••••here')."""
    s = str(key or "").strip()
    if not s:
        return True
    return any(ch in s for ch in ("•", "…")) or "***" in s


_PROBE_ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
}


def _scanner_python() -> str:
    candidate = SCANNER_DIR / ".venv" / "bin" / "python"
    if candidate.exists():
        return str(candidate)
    return PYTHON or sys.executable


def _elapsed_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def _is_known_provider(name: str) -> bool:
    return name in PROVIDER_CLASS_MAP


def _result(provider: str, success: bool, message: str, latency: int) -> dict:
    return {"provider": provider, "success": success, "message": message, "latency_ms": latency}


def _failure(provider: str, message: str, latency: int) -> dict:
    return _result(provider, False, message, latency)


def _success(provider: str, latency: int) -> dict:
    return _result(provider, True, _CONNECTED_MESSAGE, latency)


def _timeout_for(cfg: dict) -> int:
    raw = cfg.get("timeout")
    base = _TIMEOUT_FALLBACK if raw is None else int(raw)
    return max(_TIMEOUT_FALLBACK, base + _TIMEOUT_PADDING)


def _load_base_config(name: str) -> dict:
    data = read_config().get("ai_providers", {}).get(name, {}) or {}
    return dict(data)


def _apply_overlay(base: dict, body_config: dict | None) -> dict:
    if not isinstance(body_config, dict):
        return base
    for key in _OVERLAY_KEYS:
        value = body_config.get(key)
        if value is None:
            continue
        if key == "api_key" and _looks_masked_or_missing(value):
            continue
        base[key] = value
    return base


def _trim_config(cfg: dict) -> dict:
    return {k: cfg[k] for k in _OVERLAY_KEYS if k in cfg}


def _prepare_config(name: str, body_config: dict | None) -> tuple[dict, int]:
    base = _load_base_config(name)
    timeout = _timeout_for(base)
    merged = _apply_overlay(base, body_config)
    trimmed = _trim_config(merged)
    return trimmed, timeout


def _run_probe(name: str, cfg: dict, timeout: int):
    return subprocess.run(
        [_scanner_python(), str(PROBE_SCRIPT), name, json.dumps(cfg)],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(SCANNER_DIR),
        env=_PROBE_ENV,
    )


def _parse_probe_output(stdout: str) -> tuple[dict | None, str | None]:
    try:
        return json.loads(stdout or "{}"), None
    except json.JSONDecodeError:
        return None, _INVALID_PROBE_MSG


def _handle_probe_result(name: str, parsed: dict, latency: int) -> dict:
    if parsed.get("ok"):
        return _success(name, latency)
    err = parsed.get("error") or _PROBE_FAILED_MSG
    return _failure(name, str(err), latency)


def run_provider_test(name: str, body_config: dict | None = None) -> dict:
    start = time.perf_counter()
    if not _is_known_provider(name):
        return _failure(name, f"Unknown provider: {name}", 0)

    cfg, timeout = _prepare_config(name, body_config)

    if _looks_masked_or_missing(cfg.get("api_key")):
        return _failure(name, _MASKED_HINT, _elapsed_ms(start))

    try:
        proc = _run_probe(name, cfg, timeout)
    except subprocess.TimeoutExpired:
        return _failure(name, f"Connection timed out after {timeout}s", _elapsed_ms(start))
    except OSError as exc:
        return _failure(name, str(exc), _elapsed_ms(start))

    latency = _elapsed_ms(start)
    parsed, error = _parse_probe_output(proc.stdout)
    if error is not None:
        return _failure(name, error, latency)
    return _handle_probe_result(name, parsed, latency)  # type: ignore[arg-type]
