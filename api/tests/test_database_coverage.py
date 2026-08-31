import json

from api.database import finding_to_dict, get_db, init_db, job_to_dict


def test_job_to_dict_parses_args(db):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://example.com", json.dumps({"threads": 7})),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    d = job_to_dict(row)
    assert d["args"] == {"threads": 7}
    assert d["target"] == "http://example.com"
    assert "args_json" not in d


def test_finding_to_dict_variants(db):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://x.com", "{}"),
    )
    job_id = cur.lastrowid
    # with cve_refs, ai_summary, false_positive 1
    conn.execute(
        "INSERT INTO findings (job_id, cve_refs, ai_summary, false_positive) VALUES (?, ?, ?, ?)",
        (job_id, json.dumps(["CVE-1"]), "summary", 1),
    )
    # without cve_refs, false_positive 0
    conn.execute(
        "INSERT INTO findings (job_id, cve_refs, ai_summary, false_positive) VALUES (?, ?, ?, ?)",
        (job_id, None, None, 0),
    )
    # with cve_refs None and false_positive NULL
    conn.execute(
        "INSERT INTO findings (job_id, cve_refs, ai_summary, false_positive) VALUES (?, ?, ?, ?)",
        (job_id, None, None, None),
    )
    conn.commit()
    rows = conn.execute(
        "SELECT * FROM findings WHERE job_id=? ORDER BY id", (job_id,)
    ).fetchall()
    conn.close()
    d1 = finding_to_dict(rows[0])
    assert d1["cve_references"] == ["CVE-1"]
    assert d1["ai_evidence_summary"] == "summary"
    assert d1["false_positive"] is True
    assert "cve_refs" not in d1
    assert "ai_summary" not in d1
    d2 = finding_to_dict(rows[1])
    assert d2["cve_references"] is None
    assert d2["false_positive"] is False
    d3 = finding_to_dict(rows[2])
    # false_positive None leads to None (bool(None) handling)
    assert d3["false_positive"] is None


def test_init_db_idempotent(db):
    # call twice to ensure ALTER branch covered when columns already exist
    init_db()
    conn = get_db()
    row = conn.execute("SELECT count(*) as c FROM jobs").fetchone()
    assert row["c"] >= 0
    conn.close()


def test_finding_to_dict_empty_cve_refs_string(db):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO jobs (target, args_json, status) VALUES (?, ?, 'pending')",
        ("http://x.com", "{}"),
    )
    job_id = cur.lastrowid
    conn.execute("INSERT INTO findings (job_id, cve_refs) VALUES (?, ?)", (job_id, ""))
    conn.commit()
    row = conn.execute("SELECT * FROM findings WHERE job_id=?", (job_id,)).fetchone()
    conn.close()
    d = finding_to_dict(row)
    assert d["cve_references"] is None
