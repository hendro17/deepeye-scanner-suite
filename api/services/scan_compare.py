from ..database import finding_to_dict, get_db


def _match_key(finding: dict) -> str:
    fp = finding.get("fingerprint")
    if fp:
        return str(fp)
    return "|".join(
        str(finding.get(k) or "") for k in ("type", "url", "parameter")
    )


def _load_keyed_findings(job_id: int) -> dict:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM findings WHERE job_id=? ORDER BY severity, id", (job_id,)
    )
    findings = [finding_to_dict(r) for r in rows]
    conn.close()
    return {_match_key(f): f for f in findings}


def _find_severity_changes(findings_a: dict, findings_b: dict) -> tuple[int, list[dict]]:
    persisting_count = 0
    severity_changes = []
    for k, fb in findings_b.items():
        fa = findings_a.get(k)
        if fa is None:
            continue
        persisting_count += 1
        sev_a = fa.get("severity") or ""
        sev_b = fb.get("severity") or ""
        if sev_a != sev_b:
            severity_changes.append({
                "type": fb.get("type"),
                "url": fb.get("url"),
                "parameter": fb.get("parameter"),
                "severity_a": fa.get("severity"),
                "severity_b": fb.get("severity"),
            })
    return persisting_count, severity_changes


def _job_meta(row: dict) -> dict:
    return {"id": row["id"], "target": row["target"], "status": row["status"]}


def compare_scans(job_a, job_b) -> dict:
    a = _load_keyed_findings(job_a["id"])
    b = _load_keyed_findings(job_b["id"])

    new = [f for k, f in b.items() if k not in a]
    resolved = [f for k, f in a.items() if k not in b]
    persisting_count, severity_changes = _find_severity_changes(a, b)

    return {
        "scan_a": _job_meta(job_a),
        "scan_b": _job_meta(job_b),
        "new_vulnerabilities": new,
        "resolved_vulnerabilities": resolved,
        "new_count": len(new),
        "resolved_count": len(resolved),
        "persisting_count": persisting_count,
        "severity_changes": severity_changes,
    }
