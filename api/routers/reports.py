from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..database import REPORTS_DIR
from ..services.report_store import list_reports

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
async def get_reports():
    return list_reports()


@router.get("/{filename}", responses={404: {"description": "Report not found"}})
async def download_report(filename: str):
    path = REPORTS_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "Report not found")
    return FileResponse(path, filename=filename)
