import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCANNER_DIR = PROJECT_ROOT / "scanner" / "deep-eye"
CONFIG_PATH = SCANNER_DIR / "config" / "config.yaml"
REPORTS_DIR = SCANNER_DIR / "reports"
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "suite.db"
PYTHON = str(PROJECT_ROOT / ".venv" / "bin" / "python")


def get_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            target      TEXT NOT NULL,
            args_json   TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'pending',
            pid         INTEGER,
            report_path TEXT,
            started_at  TEXT,
            ended_at    TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS findings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id      INTEGER NOT NULL,
            type        TEXT,
            severity    TEXT,
            url         TEXT,
            parameter   TEXT,
            payload     TEXT,
            evidence    TEXT,
            remediation TEXT,
            fingerprint TEXT,
            cve_refs    TEXT,
            ai_summary  TEXT,
            false_positive INTEGER,
            description TEXT,
            screenshot  TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        );
        CREATE INDEX IF NOT EXISTS idx_findings_job ON findings(job_id);
        CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
    """)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(findings)").fetchall()}
    for col, coltype in [("description", "TEXT"), ("screenshot", "TEXT")]:
        if col not in cols:
            conn.execute(f"ALTER TABLE findings ADD COLUMN {col} {coltype}")
    conn.close()


def job_to_dict(row: sqlite3.Row) -> dict:
    import json

    d = dict(row)
    d["args"] = json.loads(d.pop("args_json", "{}"))
    return d


def finding_to_dict(row: sqlite3.Row) -> dict:
    import json

    d = dict(row)
    if d.get("cve_refs"):
        d["cve_references"] = json.loads(d.pop("cve_refs"))
    else:
        d["cve_references"] = None
        d.pop("cve_refs", None)
    d["ai_evidence_summary"] = d.pop("ai_summary", None)
    d["false_positive"] = (
        bool(d.pop("false_positive", 0))
        if d.get("false_positive") is not None
        else None
    )
    return d
