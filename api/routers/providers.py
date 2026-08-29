from fastapi import APIRouter
from pydantic import BaseModel

from ..services.config_service import get_provider_status
from ..services.provider_test import run_provider_test

router = APIRouter(prefix="/api/providers", tags=["providers"])


class ProviderTestRequest(BaseModel):
    config: dict | None = None


@router.get("/status")
async def provider_status():
    return get_provider_status()


@router.post("/test/{name}")
def test_provider(name: str, request: ProviderTestRequest | None = None):
    # plain def (not async) so FastAPI runs this blocking subprocess in the threadpool
    body_config = request.config if request else None
    return run_provider_test(name, body_config)
