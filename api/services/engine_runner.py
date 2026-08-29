import asyncio
import json
import queue
import re
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

from ..database import (
    CONFIG_PATH,
    DATA_DIR,
    PYTHON,
    REPORTS_DIR,
    SCANNER_DIR,
    get_db,
)
from . import report_store

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

active_scans: dict[int, dict] = {}


def _load_base_config() -> dict:
    import yaml

    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH) as f:
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


def _build_login_macro(job_id: int, job_args: dict, base_cfg: dict) -> None:
    import json as _json

    login_url = job_args.get("login_url") or job_args.get("target_url")
    username = job_args.get("login_username") or ""
    password = job_args.get("login_password") or ""
    u_field = job_args.get("login_username_field") or "username"
    p_field = job_args.get("login_password_field") or "password"
    target_url = job_args.get("target_url")
    macro_dir = Path(DATA_DIR) / "tmp_scans" / str(job_id)
    macro_dir.mkdir(parents=True, exist_ok=True)
    macro_path = macro_dir / "login_macro.json"
    macro = {
        "steps": [
            {"action": "get", "url": login_url},
            {
                "action": "extract_csrf",
                "from": 'input[name="csrf_token"]',
                "save_as": "csrf_token",
            },
            {
                "action": "extract_csrf",
                "from": 'input[name="_token"]',
                "save_as": "csrf_token2",
            },
            {
                "action": "extract_csrf",
                "from": 'input[name="authenticity_token"]',
                "save_as": "csrf_token3",
            },
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
            },
        ],
        "auth_check": {"url": target_url, "must_not_contain": "login"},
    }
    with open(macro_path, "w") as f:
        _json.dump(macro, f, indent=2)
    try:
        macro_path.chmod(0o600)
    except OSError:
        pass  # NOSONAR - best-effort permission hardening
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
        return CONFIG_PATH
    base_cfg = _load_base_config()
    base_cfg.setdefault("scanner", {})
    if auth_mode == "cookie_headers":
        _build_cookie_headers_config(base_cfg, job_args)
    elif auth_mode == "form_login":
        _build_login_macro(job_id, job_args, base_cfg)
    tmp_dir = Path(DATA_DIR) / "tmp_scans" / str(job_id)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / "config.yaml"
    with open(tmp_path, "w") as f:
        yaml.safe_dump(base_cfg, f, sort_keys=False)
    try:
        tmp_path.chmod(0o600)
    except OSError:
        pass  # NOSONAR - best-effort permission hardening
    return tmp_path


def build_cmd(job_args: dict) -> list[str]:
    job_id = job_args.get("_job_id", 0)
    config_path = (
        _build_temp_config(job_id, job_args)
        if job_args.get("auth_mode", "none") != "none"
        else CONFIG_PATH
    )
    # Store resolved path for cleanup/debugging
    job_args["_resolved_config"] = str(config_path)
    cmd = [
        PYTHON,
        str(SCANNER_DIR / "deep_eye.py"),
        "-u",
        job_args["target_url"],
        "-c",
        str(config_path),
        "--no-banner",
    ]
    if job_args.get("formats"):
        cmd.extend(["--formats", ",".join(job_args["formats"])])
    if job_args.get("scope_nl"):
        cmd.extend(["--scope-nl", job_args["scope_nl"]])
    return cmd


def start_scan(job_id: int, job_args: dict) -> int:
    # Inject job_id for temp config generation
    job_args["_job_id"] = job_id
    cmd = build_cmd(job_args)
    before = set()
    if REPORTS_DIR.exists():
        before = {f.name for f in REPORTS_DIR.iterdir()}

    process = subprocess.Popen(
        cmd,
        cwd=str(SCANNER_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    q: queue.Queue = queue.Queue()
    active_scans[job_id] = {
        "process": process,
        "queue": q,
        "done": False,
        "exit_code": None,
        "pid": process.pid,
        "before_files": before,
    }

    def reader():
        for line in process.stdout:
            clean = ANSI_RE.sub("", line.rstrip())
            ts = datetime.now(timezone.utc).isoformat()
            q.put(("log", clean, ts))
        process.wait()
        exit_code = process.returncode
        active_scans[job_id]["done"] = True
        active_scans[job_id]["exit_code"] = exit_code
        report_path = _finalize_scan(job_id, exit_code, before)
        q.put(("done", report_path, exit_code))

    threading.Thread(target=reader, daemon=True).start()
    return process.pid


def _resolve_report_path(before: set[str]) -> str | None:
    if not REPORTS_DIR.exists():
        return None
    after = {f.name for f in REPORTS_DIR.iterdir()}
    new_files = after - before
    json_files = [
        f for f in new_files if f.endswith(".json") and not f.endswith(".sarif.json")
    ]
    if not json_files:
        return None
    return str(REPORTS_DIR / max(json_files))


def _persist_job_status(job_id: int, exit_code: int, report_path: str | None) -> None:
    ended = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute(
        "UPDATE jobs SET status=?, report_path=?, ended_at=? WHERE id=?",
        ("completed" if exit_code == 0 else "failed", report_path, ended, job_id),
    )
    conn.commit()
    conn.close()
    if report_path:
        report_store.parse_findings(job_id, Path(report_path))


def _cleanup_tmp_scan_dir(job_id: int) -> None:
    try:
        import shutil

        tmp_scan_dir = Path(DATA_DIR) / "tmp_scans" / str(job_id)
        if tmp_scan_dir.is_dir():
            shutil.rmtree(tmp_scan_dir, ignore_errors=True)
    except OSError:
        pass  # NOSONAR - best-effort cleanup


def _finalize_scan(job_id: int, exit_code: int, before: set[str]) -> str | None:
    report_path = _resolve_report_path(before)
    _persist_job_status(job_id, exit_code, report_path)
    _cleanup_tmp_scan_dir(job_id)
    return report_path


def stop_scan(job_id: int) -> bool:
    scan = active_scans.get(job_id)
    if not scan or not scan["process"]:
        return False
    process = scan["process"]
    try:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    except ProcessLookupError:
        pass  # NOSONAR - process already exited
    scan["done"] = True
    conn = get_db()
    conn.execute(
        "UPDATE jobs SET status='stopped', ended_at=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), job_id),
    )
    conn.commit()
    conn.close()
    return True


async def stream_scan(job_id: int):
    scan = active_scans.get(job_id)
    if not scan:
        yield 'event: error\ndata: {"message": "Scan not found or not running"}\n\n'
        return

    q = scan["queue"]
    while True:
        try:
            item = await asyncio.to_thread(q.get, True, 1.0)
            event_type, data, extra = item
            if event_type == "log":
                payload = json.dumps({"line": data, "timestamp": extra})
                yield f"event: log\ndata: {payload}\n\n"
            elif event_type == "done":
                payload = json.dumps({"exit_code": extra, "report_path": data})
                yield f"event: done\ndata: {payload}\n\n"
                break
        except queue.Empty:
            if scan["done"]:
                break
            yield ": keepalive\n\n"
