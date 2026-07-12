from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database.models import WebsiteScan, SecurityFinding, SavedWebsite
from backend.auth.security import get_current_user
from backend.services.scan_service import run_full_scan
from backend.services.findings import extract_findings

router = APIRouter(prefix="/api/scan", tags=["Scanner"])

class ScanRequest(BaseModel):
    url: str

@router.post("")
def create_scan(req: ScanRequest, db: Session = Depends(get_db),
                user=Depends(get_current_user)):
    try:
        data = run_full_scan(req.url)
    except Exception as e:
        raise HTTPException(400, f"Scan failed: {e}")

    scan = WebsiteScan(user_id=user.id, url=data["url"], full_url=data["full_url"],
                       score=data["score"], risk_level=data["risk"], result=data)
    db.add(scan); db.commit(); db.refresh(scan)

    for fd in extract_findings(data):
        db.add(SecurityFinding(scan_id=scan.id, **fd))
    db.commit()

    return {"id": scan.id, "created_at": scan.created_at, **data}

@router.get("/history")
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    scans = db.query(WebsiteScan).filter(WebsiteScan.user_id == user.id)\
              .order_by(WebsiteScan.created_at.desc()).all()
    return [{"id": s.id, "url": s.url, "score": s.score,
             "risk": s.risk_level, "date": s.created_at} for s in scans]

@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(WebsiteScan).filter(WebsiteScan.id == scan_id,
                                     WebsiteScan.user_id == user.id).first()
    if not s: raise HTTPException(404, "Scan not found")
    return {"id": s.id, "date": s.created_at, **s.result}

@router.delete("/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(WebsiteScan).filter(WebsiteScan.id == scan_id,
                                     WebsiteScan.user_id == user.id).first()
    if not s: raise HTTPException(404, "Scan not found")
    db.delete(s); db.commit()
    return {"deleted": True}