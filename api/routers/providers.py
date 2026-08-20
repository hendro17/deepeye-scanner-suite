from fastapi import APIRouter

from ..services.config_service import get_provider_status

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("/status")
async def provider_status():
    return get_provider_status()


@router.post("/test/{name}")
async def test_provider(name: str):
    return {"success": False, "error": "Not implemented in Phase 1"}
