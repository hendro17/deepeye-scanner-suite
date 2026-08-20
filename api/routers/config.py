from fastapi import APIRouter
from pydantic import BaseModel

from ..services.config_service import read_config, write_config, mask_config

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdate(BaseModel):
    config: dict


@router.get("")
async def get_config():
    raw = read_config()
    return {"config": mask_config(raw), "masked": True}


@router.put("")
async def update_config(body: ConfigUpdate):
    write_config(body.config)
    return {"success": True}
