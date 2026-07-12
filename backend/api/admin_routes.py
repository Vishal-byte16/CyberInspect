from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User, WebsiteScan, AdminLog
from backend.auth.security import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/stats")
def stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    scans = db.query(WebsiteScan).all()
    avg = round(sum(s.score for s in scans) / len(scans)) if scans else 0
    return {"users": db.query(User).count(), "scans": len(scans),
            "avg_score": avg,
            "high_risk": sum(1 for s in scans if s.risk_level in ("High", "Critical"))}

@router.get("/users")
def users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role,
             "joined": u.created_at,
             "scans": len(u.scans)} for u in db.query(User).all()]

@router.delete("/users/{uid}")
def del_user(uid: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if uid == admin.id: raise HTTPException(400, "Cannot delete yourself")
    u = db.query(User).get(uid)
    if not u: raise HTTPException(404, "User not found")
    db.delete(u)
    db.add(AdminLog(actor_id=admin.id, action="delete_user", target=u.email))
    db.commit()
    return {"deleted": True}