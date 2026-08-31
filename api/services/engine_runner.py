import asyncio
import json
import queue
import re
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

from ..database import CONFIG_PATH, DATA_DIR, PYTHON, REPORTS_DIR, SCANNER_DIR, get_db
from . import report_store

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

active_scans: dict[int, dict] = {}


# ---- Auth helpers: delegated to scan_auth to lower file Overall complexity ----
# Wrappers sync monkeypatched CONFIG_PATH/DATA_DIR (tests patch engine_runner globals)
# to the underlying module (which reads via api.database) so patching either place works.


def _load_base_config() -> dict:
    import api.database as _db

    _db.CONFIG_PATH = CONFIG_PATH
    _db.DATA_DIR = DATA_DIR
    import api.services.scan_auth as _sa

    return _sa._load_base_config()


def _build_cookie_headers_config(base_cfg: dict, job_args: dict) -> None:
    import api.services.scan_auth as _sa

    return _sa._build_cookie_headers_config(base_cfg, job_args)


def _build_login_macro(job_id: int, job_args: dict, base_cfg: dict) -> None:
    import api.database as _db

    _db.DATA_DIR = DATA_DIR
    _db.CONFIG_PATH = CONFIG_PATH
    import api.services.scan_auth as _sa

    return _sa._build_login_macro(job_id, job_args, base_cfg)


def _build_temp_config(job_id: int, job_args: dict) -> Path:
    import api.database as _db

    _db.CONFIG_PATH = CONFIG_PATH
    _db.DATA_DIR = DATA_DIR
    import api.services.scan_auth as _sa

    return _sa._build_temp_config(job_id, job_args)


def build_cmd(job_args: dict) -> list[str]:
    job_id = job_args.get("_job_id", 0)
    config_path = (
        _build_temp_config(job_id, job_args)
        if job_args.get("auth_mode", "none") != "none"
        else CONFIG_PATH
    )
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
        pass  # NOSONAR


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
        pass  # NOSONAR
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
