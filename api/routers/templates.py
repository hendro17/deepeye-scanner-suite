import time
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from ..database import SCANNER_DIR

router = APIRouter(prefix="/api/templates", tags=["templates"])

TEMPLATES_DIR = SCANNER_DIR / "templates"
CUSTOM_DIR = TEMPLATES_DIR / "custom"

YAML_PATTERN = "*.yaml"


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
    for p in TEMPLATES_DIR.rglob(YAML_PATTERN):
        try:
            with open(p) as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(data, dict) and str(data.get("id") or "") == template_id:
            return p, data
    return None, None


def _parse_yaml(content: str) -> object:
    """Parse YAML, raise 400 on syntax error."""
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as ye:
        raise HTTPException(
            status_code=400, detail=f"YAML parse error: {ye}"
        ) from ye  # NOSONAR - helper raise documented via route responses


def _validate_dict(data: object) -> None:
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400, detail="Template top-level must be mapping"
        )  # NOSONAR - helper raise documented via route responses


def _validate_required_fields(data: dict) -> None:
    for k in ("id", "info", "http"):
        if k not in data:
            raise HTTPException(
                status_code=400, detail=f"missing required field '{k}'"
            )  # NOSONAR - helper raise documented via route responses


def _validate_id_match(data: dict, effective_source: str) -> None:
    # No-op when source is generic; reserved for strict id/source check
    if effective_source == "<inline>":
        return
    # parser already validates; fallback keeps minimal check
    return


def _validate_info(data: dict) -> None:
    info = data.get("info")
    if not isinstance(info, dict):
        raise HTTPException(
            status_code=400, detail="missing required field 'info'"
        )  # NOSONAR - helper raise documented via route responses
    if not str(info.get("name") or "").strip():
        raise HTTPException(
            status_code=400, detail="info.name is required"
        )  # NOSONAR - helper raise documented via route responses


def _validate_http_array(data: dict) -> None:
    http = data.get("http")
    if not isinstance(http, list) or len(http) == 0:
        raise HTTPException(
            status_code=400, detail="http must be non-empty list"
        )  # NOSONAR - helper raise documented via route responses


def _validate_severity(data: dict) -> None:
    sev = (
        str(data.get("info", {}).get("severity") or "").lower()
        if isinstance(data.get("info"), dict)
        else ""
    )
    if sev and sev not in {"info", "low", "medium", "high", "critical"}:
        raise HTTPException(
            status_code=400, detail=f"invalid severity '{sev}'"
        )  # NOSONAR - helper raise documented via route responses


def _validate_matchers(data: dict) -> None:
    http = data.get("http")
    if not isinstance(http, list):
        return
    for block in http:
        if not isinstance(block, dict):
            continue
        matchers = block.get("matchers")
        if matchers is None:
            continue
        if not isinstance(matchers, list):
            raise HTTPException(
                status_code=400, detail="matchers must be list"
            )  # NOSONAR - helper raise documented via route responses


def _try_parse_via_engine(content: str, effective_source: str) -> dict | None:
    """Try template_engine parser. Return dict on success, None if engine unavailable, raise 400 on engine validation fail."""
    import sys

    scanner_root = str(SCANNER_DIR)
    if scanner_root not in sys.path:
        sys.path.insert(0, scanner_root)
    try:
        from modules.template_engine.parser import parse_template  # type: ignore  # noqa: I001
    except ImportError:
        return None
    try:
        return parse_template(content, source_path=effective_source)  # type: ignore[no-untyped-call]
    except Exception as exc:  # NOSONAR - parser validation errors map to 400
        msg = str(exc)
        raise HTTPException(
            status_code=400, detail=msg
        ) from exc  # NOSONAR - helper raise documented via route responses


def _validate_via_fallback(content: str, effective_source: str) -> dict:
    data = _parse_yaml(content)
    _validate_dict(data)
    _validate_required_fields(data)  # type: ignore[arg-type]
    _validate_id_match(data, effective_source)  # type: ignore[arg-type]
    _validate_info(data)  # type: ignore[arg-type]
    _validate_http_array(data)  # type: ignore[arg-type]
    _validate_severity(data)  # type: ignore[arg-type]
    _validate_matchers(data)  # type: ignore[arg-type]
    return data  # type: ignore[return-value]


def _resolve_effective_source(source_path: str, source: str | None) -> str:
    if source is not None:
        return source
    return source_path


def _validate_content(
    content: str, source_path: str = "<inline>", source: str | None = None
) -> dict:
    """Validate via template_engine/parser.py parse_template. Raise HTTPException 400 on fail."""
    effective_source = _resolve_effective_source(source_path, source)
    engine_result = _try_parse_via_engine(content, effective_source)
    if engine_result is not None:
        return engine_result
    return _validate_via_fallback(content, effective_source)


def _passes_tag_filter(data: dict, tag_filters: list) -> bool:
    if not tag_filters:
        return True
    tags = _extract_tags(data)
    return any(t in tag_filters for t in tags)


def _passes_severity_filter(data: dict, severity_filter: list) -> bool:
    if not severity_filter:
        return True
    sev = _extract_severity(data)
    return sev in [str(s).lower() for s in severity_filter]


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
    if not _passes_tag_filter(data, tag_filters):
        return False
    if not _passes_severity_filter(data, severity_filter):  # noqa: SIM103
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
    for path in sorted(TEMPLATES_DIR.rglob(YAML_PATTERN)):
        templates.append(_entry_for_path(path))
    return templates


@router.post("/reload")
def reload_templates():
    # Stateless: just recount — loader reads disk on scan start, no cache to bust
    count = 0
    if TEMPLATES_DIR.is_dir():
        count = sum(1 for _ in TEMPLATES_DIR.rglob(YAML_PATTERN))
    return {"count": count, "reloaded": True}


@router.get(
    "/{template_id}",
    responses={
        404: {"description": "Template not found"},
        500: {"description": "Read error"},
    },
)
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


def _require_content(body: dict) -> str:
    content = body.get("content") or body.get("yaml") or ""
    if not content or not isinstance(content, str):
        raise HTTPException(status_code=400, detail="content (YAML string) required")
    return content


def _ensure_size_ok(content: str) -> None:
    if len(content.encode("utf-8")) > 50 * 1024:
        raise HTTPException(status_code=400, detail="template exceeds 50KB limit")


def _resolve_template_id(body: dict, parsed: dict) -> str:
    explicit_id = body.get("id")
    parsed_id = str(parsed.get("id") or "")
    if explicit_id and str(explicit_id) != parsed_id:
        raise HTTPException(
            status_code=400,
            detail=f"id mismatch: body.id '{explicit_id}' != yaml id '{parsed_id}'",
        )
    tid = parsed_id or str(explicit_id or "")
    if not tid:
        raise HTTPException(status_code=400, detail="template id required")
    return tid


def _ensure_not_exists(tid: str) -> None:
    existing_path, _ = _find_by_id(tid)
    if existing_path is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Template id '{tid}' already exists at {existing_path.relative_to(SCANNER_DIR).as_posix()}",
        )


def _write_custom_template(tid: str, content: str) -> Path:
    cdir = _custom_dir()
    dest = cdir / f"{tid}.yaml"
    if dest.resolve().parent != cdir.resolve():
        raise HTTPException(status_code=400, detail="invalid id")
    dest.write_text(content, encoding="utf-8")
    return dest


def _require_content_for_update(body: dict) -> str:
    return _require_content(body)


def _ensure_update_size_ok(content: str) -> None:
    _ensure_size_ok(content)


def _find_existing_or_404(template_id: str) -> Path:
    path, _ = _find_by_id(template_id)
    if path is None:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_id}' not found"
        )
    return path


def _ensure_not_shipped(path: Path) -> None:
    if _is_shipped(path):
        raise HTTPException(
            status_code=403,
            detail="shipped templates are protected — duplicate to custom/ first",
        )


def _validate_update_content(content: str, template_id: str) -> dict:
    parsed = _validate_content(content, source_path=template_id)
    parsed_id = str(parsed.get("id") or "")
    if parsed_id and parsed_id != template_id:
        raise HTTPException(
            status_code=400,
            detail=f"id mismatch: URL id '{template_id}' != yaml id '{parsed_id}'",
        )
    return parsed


def _backup_template(path: Path) -> None:
    try:
        bak = path.with_suffix(f".yaml.bak.{int(time.time())}")
        bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        pass  # NOSONAR - best-effort backup, ignore


@router.post(
    "",
    status_code=201,
    responses={
        400: {"description": "Bad Request"},
        409: {"description": "Conflict"},
    },
)
def create_template(body: dict):
    content = _require_content(body)
    _ensure_size_ok(content)
    explicit_id = body.get("id")
    parsed = _validate_content(content, source_path=explicit_id or "<inline>")
    tid = _resolve_template_id(body, parsed)
    _ensure_not_exists(tid)
    dest = _write_custom_template(tid, content)
    return {"id": tid, "path": dest.relative_to(SCANNER_DIR).as_posix()}


@router.put(
    "/{template_id}",
    responses={
        400: {"description": "Bad Request"},
        403: {"description": "Forbidden — shipped template protected"},
        404: {"description": "Template not found"},
    },
)
def update_template(template_id: str, body: dict):
    content = _require_content_for_update(body)
    _ensure_update_size_ok(content)
    path = _find_existing_or_404(template_id)
    _ensure_not_shipped(path)
    _validate_update_content(content, template_id)
    _backup_template(path)
    path.write_text(content, encoding="utf-8")
    return {"id": template_id, "path": path.relative_to(SCANNER_DIR).as_posix()}


@router.delete(
    "/{template_id}",
    status_code=204,
    responses={
        403: {"description": "Forbidden — shipped template protected"},
        404: {"description": "Template not found"},
        500: {"description": "Delete error"},
    },
)
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
