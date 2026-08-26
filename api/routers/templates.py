import yaml
from fastapi import APIRouter

from ..database import SCANNER_DIR

router = APIRouter(prefix="/api/templates", tags=["templates"])

TEMPLATES_DIR = SCANNER_DIR / "templates"


def _extract_tags(data: object) -> list[str]:
    info = data.get("info") if isinstance(data, dict) else None
    tags = info.get("tags") if isinstance(info, dict) else None
    if not isinstance(tags, list):
        return []
    return [str(tag) for tag in tags]


@router.get("")
def list_templates():
    if not TEMPLATES_DIR.is_dir():
        return []
    templates = []
    for path in sorted(TEMPLATES_DIR.rglob("*.yaml")):
        entry = {
            "name": path.stem,
            "path": path.relative_to(SCANNER_DIR).as_posix(),
            "tags": [],
        }
        try:
            with open(path) as f:
                entry["tags"] = _extract_tags(yaml.safe_load(f))
        except (OSError, yaml.YAMLError):
            pass
        templates.append(entry)
    return templates
