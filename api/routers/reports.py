from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..services.report_store import list_reports
from ..database import REPORTS_DIR

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
async def get_reports(scan_id: int | None = None):
    return list_reports(scan_id)


@router.get("/{filename}")
async def download_report(filename: str):
    path = REPORTS_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "Report not found")
    return FileResponse(path, filename=filename)
