import json
from datetime import datetime, timezone
from urllib.parse import urlparse

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from starlette.responses import StreamingResponse

from ..database import get_db, job_to_dict
from ..services import engine_runner, report_store, scan_compare

router = APIRouter(prefix="/api/scans", tags=["scans"])


class ScanCreate(BaseModel):
    target_url: str
    scope_nl: str | None = None
    checks: list[str] | None = None
    threads: int = 5
    depth: int = 2
    formats: list[str] | None = None
    extra_flags: dict | None = None
    enable_recon: bool = False
    full_scan: bool = False
    quick_scan: bool = False
    scan_subdomains: bool = False
    secrets_enabled: bool = False
    secret_patterns: list[str] | None = None

    @field_validator("target_url")
    @classmethod
    def validate_url(cls, v):
        if "://" not in v:
            v = f"https://{v}"
        if urlparse(v).scheme not in ("http", "https"):
            raise ValueError("target_url must use an http or https scheme")
        return v

    @field_validator("formats")
    @classmethod
    def validate_formats(cls, v):
        if v is None:
            return v
        cleaned = [f.strip().lower() for f in v if f.strip()]
        if "json" not in cleaned:
            cleaned.append("json")
        return cleaned

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


class ScanCompare(BaseModel):
    scan_id_a: int
    scan_id_b: int


class OpenApiIngest(BaseModel):
    filename: str
    content: str


def _parse_spec(content: str) -> dict:
    try:
        spec = json.loads(content)
    except json.JSONDecodeError:
        try:
            spec = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise HTTPException(400, f"Invalid JSON/YAML spec: {exc}") from exc
    if not isinstance(spec, dict):
        raise HTTPException(400, "Spec must be a JSON or YAML object")
    return spec


def _normalize_base(url: str) -> str | None:
    cleaned = url.strip().rstrip("/")
    parsed = urlparse(cleaned)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return cleaned
    return None


def _extract_v3_bases(servers: list) -> list[str]:
    bases = []
    for server in servers:
        if isinstance(server, dict):
            base = _normalize_base(str(server.get("url", "")))
            if base:
                bases.append(base)
    return bases


def _extract_v2_base(spec: dict) -> str | None:
    if not spec.get("host"):
        return None
    schemes = spec.get("schemes") or ["https"]
    scheme = schemes[0] if isinstance(schemes, list) and schemes else "https"
    base_path = str(spec.get("basePath") or "").rstrip("/")
    return _normalize_base(f"{scheme}://{spec['host']}{base_path}")


def _extract_bases(spec: dict) -> list[str]:
    servers = spec.get("servers")
    if isinstance(servers, list):
        bases = _extract_v3_bases(servers)
        if bases:
            return bases
    v2_base = _extract_v2_base(spec)
    return [v2_base] if v2_base else []


def _extract_paths(spec: dict) -> list[str]:
    raw_paths = spec.get("paths") or {}
    if not isinstance(raw_paths, dict):
        return []
    return [p for p in raw_paths if isinstance(p, str) and p.startswith("/")]


def _build_targets(bases: list[str], paths: list[str]) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()
    for base in bases:
        for path in paths:
            url = f"{base}/{path.lstrip('/')}"
            if url not in seen:
                seen.add(url)
                targets.append(url)
    return targets


@router.post("/ingest-openapi", responses={400: {"description": "Invalid JSON/YAML spec"}})
async def ingest_openapi(body: OpenApiIngest):
    spec = _parse_spec(body.content)
    bases = _extract_bases(spec)
    paths = _extract_paths(spec)
    targets = _build_targets(bases, paths)
    return {"targets": targets, "count": len(targets)}


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
    sev_rows = conn.execute(
        "SELECT job_id, severity, COUNT(*) AS c FROM findings GROUP BY job_id, severity"
    ).fetchall()
    conn.close()
    counts: dict[int, dict[str, int]] = {}
    for r in sev_rows:
        entry = counts.setdefault(
            r["job_id"], {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        )
        sev = r["severity"] if r["severity"] in entry else "info"
        entry[sev] += r["c"]
    zero = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    result = []
    for r in rows:
        d = job_to_dict(r)
        d["severity_counts"] = counts.get(d["id"], zero)
        result.append(d)
    return result


@router.post("/compare", responses={404: {"description": "Scan not found"}})
async def compare_scans(body: ScanCompare):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM jobs WHERE id IN (?, ?)", (body.scan_id_a, body.scan_id_b)
    ).fetchall()
    conn.close()
    by_id = {r["id"]: r for r in rows}
    for sid in (body.scan_id_a, body.scan_id_b):
        if sid not in by_id:
            raise HTTPException(404, f"Scan {sid} not found")
    return scan_compare.compare_scans(by_id[body.scan_id_a], by_id[body.scan_id_b])


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
        (pid, datetime.now(timezone.utc).isoformat(), job_id),
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
