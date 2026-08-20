import subprocess
from fastapi import APIRouter

from ..database import PYTHON, SCANNER_DIR

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.post("/update-cve")
async def update_cve():
    process = subprocess.Popen(
        [PYTHON, str(SCANNER_DIR / "scripts" / "update_cve_database.py")],
        cwd=str(SCANNER_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {"status": "started", "pid": process.pid}


@router.post("/build-rag")
async def build_rag():
    process = subprocess.Popen(
        [PYTHON, str(SCANNER_DIR / "scripts" / "build_cve_rag_index.py")],
        cwd=str(SCANNER_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {"status": "started", "pid": process.pid}
