import json
from datetime import datetime
from pathlib import Path

from ..database import REPORTS_DIR, get_db, finding_to_dict


def parse_findings(job_id: int, json_path: Path) -> int:
    with open(json_path) as f:
        data = json.load(f)

    if isinstance(data, list):
        vulns = data
    else:
        vulns = data.get("vulnerabilities", [])

    conn = get_db()
    for v in vulns:
        conn.execute("""
            INSERT INTO findings (job_id, type, severity, url, parameter, payload,
                                  evidence, remediation, fingerprint, cve_refs, ai_summary,
                                  false_positive, description, screenshot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            v.get("type"),
            v.get("severity"),
            v.get("url"),
            v.get("parameter"),
            v.get("payload"),
            v.get("evidence"),
            v.get("remediation"),
            v.get("fingerprint"),
            json.dumps(v.get("cve_references")) if v.get("cve_references") else None,
            v.get("ai_evidence_summary"),
            1 if v.get("false_positive") else 0,
            v.get("description"),
            v.get("screenshot"),
        ))
    conn.commit()
    conn.close()
    return len(vulns)


def list_reports() -> list[dict]:
    if not REPORTS_DIR.exists():
        return []
    files = []
    for f in sorted(REPORTS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        ext = f.suffix.lstrip(".").lower()
        if ext not in ("html", "pdf", "json", "sarif", "xml", "csv", "xlsx"):
            continue
        files.append({
            "filename": f.name,
            "format": ext,
            "size": f.stat().st_size,
            "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return files


def get_findings(job_id: int) -> dict:
    conn = get_db()
    rows = conn.execute("SELECT * FROM findings WHERE job_id=? ORDER BY severity, id", (job_id,))
    findings = [finding_to_dict(r) for r in rows]
    job = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()

    severity_counts = {}
    for f in findings:
        sev = f.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    urls_crawled = 0
    duration = None
    report_path = job["report_path"] if job else None
    if report_path:
        p = Path(report_path)
        if p.suffix == ".json" and p.exists():
            try:
                with open(p) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    urls_crawled = data.get("urls_crawled", 0)
                    duration = data.get("duration")
            except (json.JSONDecodeError, OSError):
                pass

    return {
        "vulnerabilities": findings,
        "urls_crawled": urls_crawled,
        "duration": duration,
        "total": len(findings),
        "severity_counts": severity_counts,
        "target": job["target"] if job else None,
    }
