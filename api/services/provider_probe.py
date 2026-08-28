"""Standalone probe run under the scanner venv python to test a provider API key.

argv: sys.argv[1] = provider name, sys.argv[2] = JSON provider config dict.
Prints EXACTLY one JSON object on stdout: {"ok": bool, "error": str | null}.
Always exits 0. Never print <dict> directly (Python repr is not valid JSON).
"""
import json
import sys
from pathlib import Path

# Guard against C/POSIX locale: non-ASCII error text would crash loggers/print
# with UnicodeEncodeError before we can surface the real probe error.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

CLASS_MAP = {
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

# <project>/api/services/provider_probe.py -> project root = parents[2]
SCANNER_DIR = Path(__file__).resolve().parents[2] / "scanner" / "deep-eye"

# Short greeting: cheap for fast chat models, and a valid non-4xx response frame
# proves the key works even when a reasoning model burns the budget on CoT.
PROBE_PROMPT = "hai"
PROBE_MAX_TOKENS = 64


def _emit(ok: bool, error: str | None) -> None:
    sys.stdout.write(json.dumps({"ok": ok, "error": error}) + "\n")
    sys.stdout.flush()


def main() -> None:
    if len(sys.argv) < 3:
        _emit(False, "missing args")
        return
    name = sys.argv[1]
    try:
        config = json.loads(sys.argv[2])
    except (ValueError, TypeError):
        _emit(False, "bad config")
        return
    cls_name = CLASS_MAP.get(name)
    if cls_name is None:
        _emit(False, f"unknown provider: {name}")
        return
    sys.path.insert(0, str(SCANNER_DIR))
    try:
        module = __import__(f"ai_providers.{name}_provider", fromlist=[cls_name])
        provider = getattr(module, cls_name)(config)
        provider.generate(PROBE_PROMPT, max_tokens=PROBE_MAX_TOKENS)
    except Exception as exc:
        err = str(exc)
        # 200-OK-with-no-text (reasoning model consumed the whole budget) = connection OK.
        if "empty" in err.lower() and "response" in err.lower():
            _emit(True, None)
            return
        _emit(False, err)
        return
    _emit(True, None)


if __name__ == "__main__":
    main()