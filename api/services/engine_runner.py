import asyncio
import json
import queue
import re
import signal
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

from ..database import PYTHON, SCANNER_DIR, CONFIG_PATH, REPORTS_DIR, get_db, job_to_dict
from . import report_store

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

active_scans: dict[int, dict] = {}


def build_cmd(job_args: dict) -> list[str]:
    cmd = [
        PYTHON,
        str(SCANNER_DIR / "deep_eye.py"),
        "-u", job_args["target_url"],
        "-c", str(CONFIG_PATH),
        "--no-banner",
    ]
    if job_args.get("formats"):
        cmd.extend(["--formats", ",".join(job_args["formats"])])
    if job_args.get("scope_nl"):
        cmd.extend(["--scope-nl", job_args["scope_nl"]])
    return cmd


def start_scan(job_id: int, job_args: dict) -> int:
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
        q.put(("done", None, exit_code))

        _finalize_scan(job_id, exit_code, before)

    threading.Thread(target=reader, daemon=True).start()
    return process.pid


def _finalize_scan(job_id: int, exit_code: int, before: set[str]) -> None:
    ended = datetime.now().isoformat()
    report_path = None
    if REPORTS_DIR.exists():
        after = {f.name for f in REPORTS_DIR.iterdir()}
        new_files = after - before
        json_files = [f for f in new_files if f.endswith(".json")]
        if json_files:
            report_path = str(REPORTS_DIR / sorted(json_files)[-1])
    conn = get_db()
    conn.execute(
        "UPDATE jobs SET status=?, report_path=?, ended_at=? WHERE id=?",
        ("completed" if exit_code == 0 else "failed", report_path, ended, job_id),
    )
    conn.commit()
    conn.close()
    if report_path:
        report_store.parse_findings(job_id, Path(report_path))


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
        pass
    scan["done"] = True
    conn = get_db()
    conn.execute("UPDATE jobs SET status='stopped', ended_at=? WHERE id=?", (datetime.now().isoformat(), job_id))
    conn.commit()
    conn.close()
    return True


async def stream_scan(job_id: int):
    from starlette.requests import Request
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
                payload = json.dumps({"exit_code": extra})
                yield f"event: done\ndata: {payload}\n\n"
                break
        except queue.Empty:
            if scan["done"]:
                break
            yield ": keepalive\n\n"
