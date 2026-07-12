from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from backend.database.db import get_db
from backend.database.models import WebsiteScan
from backend.auth.security import get_current_user
from .pdf_generator import build_pdf
from .html_generator import build_html

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def _get_scan(scan_id, db, user):
    s = db.query(WebsiteScan).filter(WebsiteScan.id == scan_id,
                                     WebsiteScan.user_id == user.id).first()
    if not s: raise HTTPException(404, "Scan not found")
    return s

@router.get("/{scan_id}/html", response_class=HTMLResponse)
def report_html(scan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return build_html(_get_scan(scan_id, db, user))

@router.get("/{scan_id}/pdf")
def report_pdf(scan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = _get_scan(scan_id, db, user)
    buf = BytesIO(build_pdf(scan))
    return StreamingResponse(buf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=CyberInspect_{scan.url}.pdf"})