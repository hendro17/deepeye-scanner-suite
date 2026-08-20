import json
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from starlette.responses import StreamingResponse

from ..database import get_db, job_to_dict
from ..services import engine_runner, report_store

router = APIRouter(prefix="/api/scans", tags=["scans"])


class ScanCreate(BaseModel):
    target_url: str
    scope_nl: str | None = None
    checks: list[str] | None = None
    threads: int = 5
    depth: int = 2
    formats: list[str] | None = None
    extra_flags: dict | None = None

    @field_validator("target_url")
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("target_url must start with http:// or https://")
        return v

    @field_validator("depth")
    @classmethod
    def validate_depth(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("depth must be 1-10")
        return v

    @field_validator("threads")
    @classmethod
    def validate_threads(cls, v):
        if not 1 <= v <= 50:
            raise ValueError("threads must be 1-50")
        return v


@router.post("")
async def create_scan(scan: ScanCreate):
    args = scan.model_dump()
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        (scan.target_url, json.dumps(args)),
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return {"id": job_id, "status": "pending"}


@router.get("")
async def list_scans():
    conn = get_db()
    rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    conn.close()
    return [job_to_dict(r) for r in rows]


@router.get("/{job_id}")
async def get_scan(job_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return {"error": "not found"}, 404
    return job_to_dict(row)


@router.post("/{job_id}/start")
async def start_scan(job_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        conn.close()
        return {"error": "not found"}, 404
    if row["status"] == "running":
        conn.close()
        return {"error": "already running"}, 409
    args = json.loads(row["args_json"])
    pid = engine_runner.start_scan(job_id, args)
    conn.execute(
        "UPDATE jobs SET status='running', pid=?, started_at=? WHERE id=?",
        (pid, datetime.now().isoformat(), job_id),
    )
    conn.commit()
    conn.close()
    return {"status": "running", "pid": pid}


@router.post("/{job_id}/stop")
async def stop_scan(job_id: int):
    engine_runner.stop_scan(job_id)
    return {"status": "stopped"}


@router.get("/{job_id}/stream")
async def stream_scan(job_id: int):
    return StreamingResponse(
        engine_runner.stream_scan(job_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{job_id}/findings")
async def get_findings(job_id: int):
    return report_store.get_findings(job_id)
