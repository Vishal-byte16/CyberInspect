from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import SavedWebsite
from backend.auth.security import get_current_user

router = APIRouter(prefix="/api/saved", tags=["Saved Websites"])

class SavedCreate(BaseModel):
    url: str

@router.get("")
def list_saved(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(SavedWebsite).filter(SavedWebsite.user_id == user.id)\
             .order_by(SavedWebsite.created_at.desc()).all()
    return [{"id": s.id, "url": s.url, "date": s.created_at} for s in rows]

@router.post("")
def add_saved(payload: SavedCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    exists = db.query(SavedWebsite).filter(SavedWebsite.user_id == user.id,
                                            SavedWebsite.url == payload.url).first()
    if exists:
        raise HTTPException(400, "Already saved")
    s = SavedWebsite(user_id=user.id, url=payload.url)
    db.add(s); db.commit(); db.refresh(s)
    return {"id": s.id, "url": s.url, "date": s.created_at}

@router.delete("/{saved_id}")
def remove_saved(saved_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(SavedWebsite).filter(SavedWebsite.id == saved_id,
                                       SavedWebsite.user_id == user.id).first()
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()
    return {"deleted": True}
