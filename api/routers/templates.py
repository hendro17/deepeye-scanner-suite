import time
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from ..database import SCANNER_DIR

router = APIRouter(prefix="/api/templates", tags=["templates"])

TEMPLATES_DIR = SCANNER_DIR / "templates"
CUSTOM_DIR = TEMPLATES_DIR / "custom"


def _custom_dir() -> Path:
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)
    return CUSTOM_DIR


def _extract_info(data: object) -> dict | None:
    if not isinstance(data, dict):
        return None
    info = data.get("info")
    return info if isinstance(info, dict) else None


def _extract_tags(data: object) -> list[str]:
    info = _extract_info(data)
    if info is None:
        return []
    tags = info.get("tags")
    if not isinstance(tags, list):
        return []
    return [str(tag) for tag in tags]


def _extract_severity(data: object) -> str:
    info = _extract_info(data)
    if info is None:
        return ""
    sev = info.get("severity")
    return str(sev).lower() if sev is not None else ""


def _http_summary(data: object) -> dict:
    if not isinstance(data, dict):
        return {"count": 0, "methods": []}
    http = data.get("http")
    if not isinstance(http, list):
        return {"count": 0, "methods": []}
    methods = []
    for block in http:
        if isinstance(block, dict) and isinstance(block.get("method"), str):
            methods.append(block["method"])
    return {"count": len(http), "methods": methods}


def _is_shipped(path: Path) -> bool:
    """True if path is NOT under custom/ — i.e. shipped template."""
    try:
        rel = path.relative_to(TEMPLATES_DIR)
    except ValueError:
        return True
    # under custom/ → not shipped
    return not str(rel).startswith("custom/") and not str(rel).startswith("custom\\")


def _find_by_id(template_id: str) -> tuple[Path | None, dict | None]:
    """Search all yaml files for matching id. Returns (path, data) or (None, None)."""
    if not TEMPLATES_DIR.is_dir():
        return None, None
    for p in TEMPLATES_DIR.rglob("*.yaml"):
        try:
            with open(p) as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(data, dict) and str(data.get("id") or "") == template_id:
            return p, data
    return None, None


def _validate_content(
    content: str, source_path: str = "<inline>", source: str | None = None
) -> dict:
    """Validate via template_engine/parser.py parse_template. Raise HTTPException 400 on fail."""
    # Lazy import to allow test monkeypatch and avoid hard dep
    import sys

    effective_source = source if source is not None else source_path
    scanner_root = str(SCANNER_DIR)
    if scanner_root not in sys.path:
        sys.path.insert(0, scanner_root)
    try:
        from modules.template_engine.parser import parse_template  # type: ignore  # noqa: I001
    except ImportError:
        # Fallback: basic yaml parse check
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as ye:
            raise HTTPException(
                status_code=400, detail=f"YAML parse error: {ye}"
            ) from ye
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=400, detail="Template top-level must be mapping"
            )
        # minimal required check
        for k in ("id", "info", "http"):
            if k not in data:
                raise HTTPException(
                    status_code=400, detail=f"missing required field '{k}'"
                )
        return data
    try:
        return parse_template(content, source_path=effective_source)
    except Exception as exc:  # NOSONAR - parser validation errors map to 400
        msg = str(exc)
        raise HTTPException(status_code=400, detail=msg) from exc


def _enabled_for(data: dict) -> bool:
    """Derive enabled via config templates.* filters."""
    from ..services.config_service import read_config

    try:
        cfg = read_config()
    except Exception:  # noqa: BLE001  # NOSONAR - config read must not break template listing
        return True
    tpl_cfg = cfg.get("templates") or {}
    if not tpl_cfg.get("enabled", False):
        return False
    tag_filters = tpl_cfg.get("tag_filters") or []
    severity_filter = tpl_cfg.get("severity_filter") or []
    if tag_filters:
        tags = _extract_tags(data)
        if not any(t in tag_filters for t in tags):
            return False
    if severity_filter:
        sev = _extract_severity(data)
        if sev not in [str(s).lower() for s in severity_filter]:
            return False
    return True


def _entry_for_path(path: Path) -> dict:
    rel = (
        path.relative_to(SCANNER_DIR).as_posix()
        if path.is_relative_to(SCANNER_DIR)
        else path.as_posix()
    )
    entry: dict = {
        "name": path.stem,
        "path": rel,
        "tags": [],
        "severity": "",
        "id": "",
        "http_count": 0,
        "enabled": False,
    }
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return entry
    if not isinstance(data, dict):
        return entry
    entry["tags"] = _extract_tags(data)
    entry["severity"] = _extract_severity(data)
    entry["id"] = str(data.get("id") or path.stem)
    hs = _http_summary(data)
    entry["http_count"] = hs["count"]
    entry["http"] = hs
    # enabled derived
    try:
        entry["enabled"] = _enabled_for(data)
    except Exception:  # noqa: BLE001  # NOSONAR - _enabled_for must not break entry rendering
        entry["enabled"] = False
    return entry


@router.get("")
def list_templates():
    if not TEMPLATES_DIR.is_dir():
        return []
    templates = []
    for path in sorted(TEMPLATES_DIR.rglob("*.yaml")):
        templates.append(_entry_for_path(path))
    return templates


@router.post("/reload")
def reload_templates():
    # Stateless: just recount — loader reads disk on scan start, no cache to bust
    count = 0
    if TEMPLATES_DIR.is_dir():
        count = sum(1 for _ in TEMPLATES_DIR.rglob("*.yaml"))
    return {"count": count, "reloaded": True}


@router.get("/{template_id}")
def get_template(template_id: str):
    path, _data = _find_by_id(template_id)
    if path is None:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_id}' not found"
        )
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {
        "id": template_id,
        "path": path.relative_to(SCANNER_DIR).as_posix(),
        "content": content,
    }


@router.post("", status_code=201)
def create_template(body: dict):
    content = body.get("content") or body.get("yaml") or ""
    if not content or not isinstance(content, str):
        raise HTTPException(status_code=400, detail="content (YAML string) required")
    if len(content.encode("utf-8")) > 50 * 1024:
        raise HTTPException(status_code=400, detail="template exceeds 50KB limit")
    # Allow explicit id override but validate consistency
    explicit_id = body.get("id")
    parsed = _validate_content(content, source_path=explicit_id or "<inline>")
    parsed_id = str(parsed.get("id") or "")
    if explicit_id and str(explicit_id) != parsed_id:
        raise HTTPException(
            status_code=400,
            detail=f"id mismatch: body.id '{explicit_id}' != yaml id '{parsed_id}'",
        )
    tid = parsed_id or str(explicit_id or "")
    if not tid:
        raise HTTPException(status_code=400, detail="template id required")
    existing_path, _ = _find_by_id(tid)
    if existing_path is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Template id '{tid}' already exists at {existing_path.relative_to(SCANNER_DIR).as_posix()}",
        )
    cdir = _custom_dir()
    dest = cdir / f"{tid}.yaml"
    # extra safety: prevent path traversal via id
    if dest.resolve().parent != cdir.resolve():
        raise HTTPException(status_code=400, detail="invalid id")
    dest.write_text(content, encoding="utf-8")
    return {"id": tid, "path": dest.relative_to(SCANNER_DIR).as_posix()}


@router.put("/{template_id}")
def update_template(template_id: str, body: dict):
    content = body.get("content") or body.get("yaml") or ""
    if not content or not isinstance(content, str):
        raise HTTPException(status_code=400, detail="content (YAML string) required")
    if len(content.encode("utf-8")) > 50 * 1024:
        raise HTTPException(status_code=400, detail="template exceeds 50KB limit")
    path, _ = _find_by_id(template_id)
    if path is None:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_id}' not found"
        )
    if _is_shipped(path):
        raise HTTPException(
            status_code=403,
            detail="shipped templates are protected — duplicate to custom/ first",
        )
    parsed = _validate_content(content, source_path=template_id)
    parsed_id = str(parsed.get("id") or "")
    if parsed_id and parsed_id != template_id:
        raise HTTPException(
            status_code=400,
            detail=f"id mismatch: URL id '{template_id}' != yaml id '{parsed_id}'",
        )
    # backup
    try:
        bak = path.with_suffix(f".yaml.bak.{int(time.time())}")
        bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        pass  # NOSONAR - best-effort backup, ignore
    path.write_text(content, encoding="utf-8")
    return {"id": template_id, "path": path.relative_to(SCANNER_DIR).as_posix()}


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: str):
    path, _ = _find_by_id(template_id)
    if path is None:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_id}' not found"
        )
    if _is_shipped(path):
        raise HTTPException(
            status_code=403, detail="shipped templates cannot be deleted"
        )
    try:
        path.unlink()
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
