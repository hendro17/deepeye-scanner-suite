"""Auth-related temp config helpers extracted from engine_runner.

Keeps macro / cookie building out of the hot file to lower Overall
Code Complexity (file-level sum). All public helpers are re-exported
via engine_runner for backwards-compat.
"""

from pathlib import Path

import api.database as db


def _load_base_config() -> dict:
    import yaml

    cfg = db.CONFIG_PATH
    if not cfg.exists():
        return {}
    try:
        with open(cfg) as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError):
        return {}


def _build_cookie_headers_config(base_cfg: dict, job_args: dict) -> None:
    headers = job_args.get("auth_headers") or {}
    cookies = job_args.get("auth_cookies") or {}
    if headers:
        merged = dict(base_cfg["scanner"].get("custom_headers") or {})
        merged.update(headers)
        base_cfg["scanner"]["custom_headers"] = merged
    if cookies:
        merged = dict(base_cfg["scanner"].get("cookies") or {})
        merged.update(cookies)
        base_cfg["scanner"]["cookies"] = merged


_CSRF_FIELDS: list[tuple[str, str]] = [
    ("csrf_token", "csrf_token"),
    ("_token", "csrf_token2"),
    ("authenticity_token", "csrf_token3"),
]


def _build_login_macro(job_id: int, job_args: dict, base_cfg: dict) -> None:
    import json as _json

    login_url = job_args.get("login_url") or job_args.get("target_url")
    username = job_args.get("login_username") or ""
    password = job_args.get("login_password") or ""
    u_field = job_args.get("login_username_field") or "username"
    p_field = job_args.get("login_password_field") or "password"
    target_url = job_args.get("target_url")
    macro_dir = Path(db.DATA_DIR) / "tmp_scans" / str(job_id)
    macro_dir.mkdir(parents=True, exist_ok=True)
    macro_path = macro_dir / "login_macro.json"
    # Build steps via loop to de-duplicate string-heavy extract_csrf blocks.
    steps: list[dict] = [{"action": "get", "url": login_url}]
    for name, save_as in _CSRF_FIELDS:
        steps.append(
            {
                "action": "extract_csrf",
                "from": f'input[name="{name}"]',
                "save_as": save_as,
            }
        )
    steps.append(
        {
            "action": "post",
            "url": login_url,
            "data": {
                u_field: username,
                p_field: password,
                "csrf_token": "${csrf_token}",
                "_token": "${csrf_token2}",
                "authenticity_token": "${csrf_token3}",
            },
        }
    )
    macro = {
        "steps": steps,
        "auth_check": {"url": target_url, "must_not_contain": "login"},
    }
    with open(macro_path, "w") as f:
        _json.dump(macro, f, indent=2)
    try:
        macro_path.chmod(0o600)
    except OSError:
        pass  # NOSONAR
    base_cfg.setdefault("login_replay", {})
    base_cfg["login_replay"]["enabled"] = True
    base_cfg["login_replay"]["macro_path"] = str(macro_path)
    base_cfg["login_replay"]["abort_on_fail"] = False
    base_cfg["login_replay"]["recheck_interval_seconds"] = 600
    base_cfg["login_replay"]["_generated_for_job"] = job_id


def _build_temp_config(job_id: int, job_args: dict) -> Path:
    """Create per-scan temp config overlay for auth. Returns path to temp yaml."""
    import yaml

    auth_mode = job_args.get("auth_mode", "none")
    if auth_mode == "none":
        return db.CONFIG_PATH
    base_cfg = _load_base_config()
    base_cfg.setdefault("scanner", {})
    if auth_mode == "cookie_headers":
        _build_cookie_headers_config(base_cfg, job_args)
    elif auth_mode == "form_login":
        _build_login_macro(job_id, job_args, base_cfg)
    tmp_dir = Path(db.DATA_DIR) / "tmp_scans" / str(job_id)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / "config.yaml"
    with open(tmp_path, "w") as f:
        yaml.safe_dump(base_cfg, f, sort_keys=False)
    try:
        tmp_path.chmod(0o600)
    except OSError:
        pass  # NOSONAR
    return tmp_path
