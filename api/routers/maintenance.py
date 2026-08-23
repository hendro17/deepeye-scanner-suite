import asyncio

from fastapi import APIRouter

from ..database import PYTHON, SCANNER_DIR

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


async def _spawn(script: str) -> int:
    process = await asyncio.create_subprocess_exec(
        PYTHON,
        str(SCANNER_DIR / "scripts" / script),
        cwd=str(SCANNER_DIR),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    return process.pid


@router.post("/update-cve")
async def update_cve():
    pid = await _spawn("update_cve_database.py")
    return {"status": "started", "pid": pid}


@router.post("/build-rag")
async def build_rag():
    pid = await _spawn("build_cve_rag_index.py")
    return {"status": "started", "pid": pid}
