"""Coverage push for api/routers/templates.py → ≥80%.
Covers: CRUD happy path + 403 shipped guard + 409 dup + 400 invalid YAML + 50KB limit.
"""

from pathlib import Path

import pytest
import yaml

from api.routers import templates as tpl

VALID_YAML = """id: test-tmpl
info:
  name: Test Template
  severity: high
  tags: [xss, sqli]
http:
  - method: GET
    path: ["{{BaseURL}}/"]
"""

VALID_YAML_2 = """id: second-tmpl
info:
  name: Second
  severity: low
  tags: [info]
http:
  - method: POST
    path: ["{{BaseURL}}/login"]
"""

INVALID_YAML_PARSE = "\t: : ["
MISSING_FIELDS_YAML = "id: lonely\ninfo:\n  name: x\n"  # missing http
SCALAR_YAML = "just-a-string"


@pytest.fixture
def tdir(monkeypatch, tmp_path):
    scanner = tmp_path / "scanner_root"
    tdir_path = scanner / "templates"
    custom = tdir_path / "custom"
    scanner.mkdir(parents=True, exist_ok=True)
    tdir_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(tpl, "SCANNER_DIR", scanner)
    monkeypatch.setattr(tpl, "TEMPLATES_DIR", tdir_path)
    monkeypatch.setattr(tpl, "CUSTOM_DIR", custom)
    monkeypatch.setattr("api.database.SCANNER_DIR", scanner)
    return scanner, tdir_path, custom


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---- helpers direct coverage ----
def test_is_shipped_true_false_and_valueerror(tdir):
    _, tdir_path, custom = tdir
    shipped = tdir_path / "shipped.yaml"
    _write(shipped, VALID_YAML)
    custom_file = custom / "my.yaml"
    _write(custom_file, VALID_YAML)
    assert tpl._is_shipped(shipped) is True
    assert tpl._is_shipped(custom_file) is False
    # ValueError path: outside TEMPLATES_DIR
    outside = Path("/tmp/outside.yaml")
    assert tpl._is_shipped(outside) is True
    # windows-style prefix guard not needed but exercised via string check
    assert tpl._is_shipped(tdir_path / "custom" / "a.yaml") is False


def test_find_by_id_missing_dir(monkeypatch, tmp_path):
    scanner = tmp_path / "scanner"
    tdir_missing = scanner / "templates"
    monkeypatch.setattr(tpl, "SCANNER_DIR", scanner)
    monkeypatch.setattr(tpl, "TEMPLATES_DIR", tdir_missing)
    # dir does not exist
    assert tpl._find_by_id("anything") == (None, None)


def test_find_by_id_rglob_and_invalid_yaml_skipped(tdir):
    _, tdir_path, _ = tdir
    _write(tdir_path / "bad.yaml", INVALID_YAML_PARSE)
    _write(tdir_path / "good.yaml", VALID_YAML)
    p, data = tpl._find_by_id("test-tmpl")
    assert p is not None and p.name == "good.yaml"
    assert data["id"] == "test-tmpl"
    assert tpl._find_by_id("nope") == (None, None)


def test_entry_for_path_all_branches(tdir, monkeypatch):
    _, tdir_path, _ = tdir
    # malformed file
    _write(tdir_path / "broken.yaml", INVALID_YAML_PARSE)
    e = tpl._entry_for_path(tdir_path / "broken.yaml")
    assert e["tags"] == [] and e["http_count"] == 0
    # scalar yaml -> not dict, returns entry with empty id
    _write(tdir_path / "scalar.yaml", SCALAR_YAML)
    e2 = tpl._entry_for_path(tdir_path / "scalar.yaml")
    assert e2["id"] == ""
    # valid with http methods
    _write(tdir_path / "valid.yaml", VALID_YAML)
    # force enabled_for to raise to test except path inside _entry_for_path
    monkeypatch.setattr(
        tpl, "_enabled_for", lambda d: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    e3 = tpl._entry_for_path(tdir_path / "valid.yaml")
    assert e3["enabled"] is False  # except branch

    # restore and test normal enabled derivation
    monkeypatch.undo()
    # config disabled path
    monkeypatch.setattr(
        "api.services.config_service.read_config",
        lambda: {"templates": {"enabled": False}},
    )
    e4 = tpl._entry_for_path(tdir_path / "valid.yaml")
    assert e4["enabled"] is False

    monkeypatch.setattr(
        "api.services.config_service.read_config",
        lambda: {
            "templates": {
                "enabled": True,
                "tag_filters": ["xss"],
                "severity_filter": ["high"],
            }
        },
    )
    e5 = tpl._entry_for_path(tdir_path / "valid.yaml")
    assert e5["enabled"] is True
    # tag mismatch
    monkeypatch.setattr(
        "api.services.config_service.read_config",
        lambda: {"templates": {"enabled": True, "tag_filters": ["nomatch"]}},
    )
    e6 = tpl._entry_for_path(tdir_path / "valid.yaml")
    assert e6["enabled"] is False


def test_enabled_for_read_config_exception(monkeypatch):
    monkeypatch.setattr(
        "api.services.config_service.read_config",
        lambda: (_ for _ in ()).throw(Exception("cfg fail")),
    )
    assert tpl._enabled_for({"info": {"tags": ["a"]}}) is True


def test_extract_severity_and_http_summary():
    assert tpl._extract_severity({"info": {"severity": "HIGH"}}) == "high"
    assert tpl._extract_severity({}) == ""
    assert tpl._extract_severity("not dict") == ""
    assert tpl._extract_severity({"info": "string"}) == ""
    assert tpl._http_summary({"http": [{"method": "GET"}, {"method": 123}, "bad"]}) == {
        "count": 3,
        "methods": ["GET"],
    }
    assert tpl._http_summary({}) == {"count": 0, "methods": []}
    assert tpl._http_summary("not dict") == {"count": 0, "methods": []}


def test_validate_content_fallback_paths(tdir):
    # force import failure by ensuring scanner_root not importable and parser unavailable
    # fallback is triggered when import fails; we test 400 cases
    # scalar top-level -> 400 must be mapping
    with pytest.raises(Exception) as ei:
        tpl._validate_content(SCALAR_YAML)
    assert ei.value.status_code == 400
    # invalid yaml parse error -> 400
    with pytest.raises(Exception) as ei2:
        tpl._validate_content(INVALID_YAML_PARSE)
    assert ei2.value.status_code == 400
    # missing required fields -> 400
    with pytest.raises(Exception) as ei3:
        tpl._validate_content(MISSING_FIELDS_YAML)
    assert "missing required field" in str(ei3.value.detail)
    # valid fallback
    data = tpl._validate_content(VALID_YAML)
    assert data["id"] == "test-tmpl"


# ---- API endpoint coverage via TestClient ----
def test_create_happy_path(client, tdir):
    r = client.post("/api/templates", json={"content": VALID_YAML})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == "test-tmpl"
    assert body["path"] == "templates/custom/test-tmpl.yaml"
    # file actually written
    _, _tdir_path, custom = tdir
    assert (custom / "test-tmpl.yaml").exists()


def test_create_409_dup(client, tdir):
    r1 = client.post("/api/templates", json={"content": VALID_YAML})
    assert r1.status_code == 201
    r2 = client.post("/api/templates", json={"content": VALID_YAML})
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"]


def test_create_400_invalid_yaml(client, tdir):
    r = client.post("/api/templates", json={"content": INVALID_YAML_PARSE})
    assert r.status_code == 400
    r2 = client.post("/api/templates", json={"content": MISSING_FIELDS_YAML})
    assert r2.status_code == 400
    assert "missing required field" in r2.json()["detail"]


def test_create_400_empty_and_50kb(client, tdir):
    r = client.post("/api/templates", json={"content": ""})
    assert r.status_code == 400
    r2 = client.post("/api/templates", json={})
    assert r2.status_code == 400
    big = (
        "id: big\ninfo:\n  name: x\n  severity: low\nhttp:\n  - method: GET\n    path: ['/']\n"
        + "x" * (51 * 1024)
    )
    r3 = client.post("/api/templates", json={"content": big})
    assert r3.status_code == 400
    assert "50KB" in r3.json()["detail"]
    # alternate key 'yaml' accepted
    r4 = client.post("/api/templates", json={"yaml": VALID_YAML_2})
    assert r4.status_code == 201


def test_create_400_id_mismatch_and_invalid_id(client, tdir):
    # explicit id mismatch
    r = client.post("/api/templates", json={"id": "other-id", "content": VALID_YAML})
    assert r.status_code == 400
    assert "mismatch" in r.json()["detail"]
    # path traversal via id containing slash attempts to escape custom dir -> 400 invalid id
    trav_yaml = VALID_YAML.replace("test-tmpl", "../evil")
    r2 = client.post("/api/templates", json={"content": trav_yaml})
    # either 400 invalid id or passes but dest parent check catches it
    assert r2.status_code == 400


def test_get_and_404(client, tdir):
    client.post("/api/templates", json={"content": VALID_YAML})
    r = client.get("/api/templates/test-tmpl")
    assert r.status_code == 200
    assert "content" in r.json()
    assert r.json()["id"] == "test-tmpl"
    r2 = client.get("/api/templates/notfound")
    assert r2.status_code == 404


def test_list_and_reload(client, tdir):
    # empty first
    r0 = client.get("/api/templates")
    assert r0.status_code == 200 and r0.json() == []
    r_reload0 = client.post("/api/templates/reload")
    assert r_reload0.json()["count"] == 0
    client.post("/api/templates", json={"content": VALID_YAML})
    client.post("/api/templates", json={"content": VALID_YAML_2})
    r = client.get("/api/templates")
    assert len(r.json()) == 2
    assert r.json()[0]["path"] < r.json()[1]["path"]  # sorted
    r_reload = client.post("/api/templates/reload")
    assert r_reload.json()["count"] == 2
    assert r_reload.json()["reloaded"] is True


def test_update_happy_and_guards(client, tdir):
    _, tdir_path, custom = tdir
    # shipped file guard
    _write(tdir_path / "shipped.yaml", VALID_YAML)
    r = client.put(
        "/api/templates/test-tmpl", json={"content": VALID_YAML.replace("high", "low")}
    )
    assert r.status_code == 403
    assert "protected" in r.json()["detail"]
    # not found
    r2 = client.put("/api/templates/missing", json={"content": VALID_YAML})
    assert r2.status_code == 404
    # create custom then update success
    client.post("/api/templates", json={"content": VALID_YAML_2})
    new_content = VALID_YAML_2.replace("low", "critical")
    r3 = client.put("/api/templates/second-tmpl", json={"content": new_content})
    assert r3.status_code == 200
    # verify file updated
    assert "critical" in (custom / "second-tmpl.yaml").read_text()
    # update with id mismatch
    bad = VALID_YAML_2.replace("second-tmpl", "other-id")
    r4 = client.put("/api/templates/second-tmpl", json={"content": bad})
    assert r4.status_code == 400
    # update 50KB guard
    big = VALID_YAML_2 + "x" * (51 * 1024)
    r5 = client.put("/api/templates/second-tmpl", json={"content": big})
    assert r5.status_code == 400
    # update with yaml key alias
    r6 = client.put("/api/templates/second-tmpl", json={"yaml": VALID_YAML_2})
    assert r6.status_code == 200
    # empty content 400
    r7 = client.put("/api/templates/second-tmpl", json={"content": ""})
    assert r7.status_code == 400


def test_delete_happy_and_guards(client, tdir):
    _, tdir_path, custom = tdir
    _write(tdir_path / "shipped2.yaml", VALID_YAML.replace("test-tmpl", "shipped2"))
    r = client.delete("/api/templates/shipped2")
    assert r.status_code == 403
    r2 = client.delete("/api/templates/notexist")
    assert r2.status_code == 404
    client.post("/api/templates", json={"content": VALID_YAML_2})
    r3 = client.delete("/api/templates/second-tmpl")
    assert r3.status_code == 204
    assert not (custom / "second-tmpl.yaml").exists()
    # verify get after delete 404
    r4 = client.get("/api/templates/second-tmpl")
    assert r4.status_code == 404


def test_validate_content_via_parser_success(monkeypatch, tdir):
    # Mock parser to test the try: parse_template branch (success)
    import sys
    import types

    fake_mod = types.ModuleType("modules.template_engine.parser")

    def fake_parse(text, source_path="<inline>"):
        return yaml.safe_load(text)

    fake_mod.parse_template = fake_parse
    fake_mod.TemplateError = Exception
    # need parent packages
    sys.modules["modules"] = types.ModuleType("modules")
    sys.modules["modules.template_engine"] = types.ModuleType("modules.template_engine")
    sys.modules["modules.template_engine.parser"] = fake_mod
    monkeypatch.setattr(
        tpl, "SCANNER_DIR", tdir[0]
    )  # ensure sys.path insert doesn't break
    data = tpl._validate_content(VALID_YAML)
    assert data["id"] == "test-tmpl"

    # failure via parser
    def fake_parse_fail(text, source_path="<inline>"):
        raise fake_mod.TemplateError("bad template")

    fake_mod.parse_template = fake_parse_fail
    with pytest.raises(Exception) as ei:
        tpl._validate_content(VALID_YAML)
    assert ei.value.status_code == 400
    # cleanup
    for k in ["modules.template_engine.parser", "modules.template_engine", "modules"]:
        sys.modules.pop(k, None)
