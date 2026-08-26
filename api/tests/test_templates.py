"""Tests for GET /api/templates (api/routers/templates.py).

The router hardcodes TEMPLATES_DIR from SCANNER_DIR, so directory-dependent
tests monkeypatch the module-level constants onto tmp_path — the same pattern
conftest.py already uses for DATA_DIR/DB_PATH.
"""

from pathlib import Path

import pytest

from api.routers import templates as templates_router


@pytest.fixture
def templates_env(monkeypatch, tmp_path):
    """Redirect the router's hardcoded template/scanner dirs into tmp_path."""
    scanner_dir = tmp_path / "deep-eye"
    templates_dir = scanner_dir / "templates"
    monkeypatch.setattr(templates_router, "TEMPLATES_DIR", templates_dir)
    monkeypatch.setattr(templates_router, "SCANNER_DIR", scanner_dir)
    return templates_dir


def _write_yaml(templates_dir, relpath, content):
    path = templates_dir / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_list_templates_returns_200_and_entry_shape(client):
    # Runs against the real scanner/deep-eye/templates when present (may be
    # absent in CI without the submodule), so only the contract is asserted.
    r = client.get("/api/templates")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    for entry in body:
        assert set(entry.keys()) == {"name", "path", "tags"}
        assert isinstance(entry["tags"], list)
        assert all(isinstance(t, str) for t in entry["tags"])
        assert entry["path"].startswith("templates/") and entry["path"].endswith(".yaml")
        assert entry["name"] == Path(entry["path"]).stem


def test_list_templates_reads_tags_from_top_level_info(client, templates_env):
    _write_yaml(
        templates_env,
        "exposures/git-config-exposure.yaml",
        """
id: git-config-exposure
info:
  name: Git Config File Exposure
  tags: [exposure, git]
http:
  - method: GET
""",
    )
    # no info block at all -> empty tags, not an error
    _write_yaml(templates_env, "misconfig/plain.yaml", "id: plain\nseverity: low\n")
    # non-yaml files must be ignored entirely
    _write_yaml(templates_env, "notes.txt", "not a template")

    r = client.get("/api/templates")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    by_name = {e["name"]: e for e in body}
    assert by_name["git-config-exposure"]["tags"] == ["exposure", "git"]
    assert by_name["git-config-exposure"]["path"] == "templates/exposures/git-config-exposure.yaml"
    assert by_name["plain"]["tags"] == []
    assert by_name["plain"]["path"] == "templates/misconfig/plain.yaml"


def test_list_templates_missing_dir_returns_empty_list(client, templates_env):
    # fixture points TEMPLATES_DIR at tmp_path but never creates it
    r = client.get("/api/templates")
    assert r.status_code == 200
    assert r.json() == []


def test_list_templates_survives_malformed_and_scalar_yaml(client, templates_env):
    _write_yaml(templates_env, "good.yaml", "info:\n  tags: [ok]\n")
    _write_yaml(templates_env, "broken.yaml", "\t: : [")  # invalid YAML syntax
    _write_yaml(templates_env, "scalar.yaml", "just-a-top-level-string\n")

    r = client.get("/api/templates")
    assert r.status_code == 200
    body = r.json()
    assert {e["name"] for e in body} == {"good", "broken", "scalar"}
    by_name = {e["name"]: e for e in body}
    assert by_name["good"]["tags"] == ["ok"]
    assert by_name["broken"]["tags"] == []
    assert by_name["scalar"]["tags"] == []


def test_list_templates_results_sorted_by_relative_path(client, templates_env):
    _write_yaml(templates_env, "zeta.yaml", "info:\n  tags: []\n")
    _write_yaml(templates_env, "nested/alpha.yaml", "info:\n  tags: []\n")
    _write_yaml(templates_env, "mid.yaml", "info:\n  tags: []\n")

    r = client.get("/api/templates")
    assert r.status_code == 200
    paths = [e["path"] for e in r.json()]
    assert paths == sorted(paths)


def test_extract_tags_semantics():
    extract = templates_router._extract_tags
    # tags live only under top-level info; nested ones are ignored
    assert extract({"info": {"tags": ["a", "b"]}, "http": [{"tags": ["ignored"]}]}) == ["a", "b"]
    # non-dict payloads and missing/mistyped fields degrade to []
    assert extract("just a string") == []
    assert extract([1, 2]) == []
    assert extract({}) == []
    assert extract({"info": "not-a-dict"}) == []
    assert extract({"info": {"tags": "single-string-not-list"}}) == []
    assert extract({"info": {}}) == []
    # list items are coerced to str
    assert extract({"info": {"tags": ["x", 3, True]}}) == ["x", "3", "True"]
