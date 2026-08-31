from fastapi import APIRouter
from pydantic import BaseModel

from ..services.config_service import (
    _merge_preserve_masked,
    mask_config,
    read_config,
    write_config,
)

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdate(BaseModel):
    config: dict


@router.get("")
async def get_config():
    raw = read_config()
    return {"config": mask_config(raw), "masked": True}


@router.put("")
async def update_config(body: ConfigUpdate):
    existing = read_config()
    # Merge incoming config onto existing, preserving real secrets when
    # frontend sends back masked placeholders (e.g. "sk-••••e2e4").
    # Without this, GET (masked) → PUT (masked blind write) corrupts disk.
    merged = _merge_preserve_masked(existing, body.config)
    write_config(merged)
    return {"success": True}
