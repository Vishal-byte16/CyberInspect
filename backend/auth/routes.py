from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User, UserProfile
from backend.auth import security, schemas

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.Token)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if len(payload.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(400, "Email already registered")
    user = User(name=payload.name, email=payload.email.lower(),
                hashed_password=security.hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    db.add(UserProfile(user_id=user.id)); db.commit()
    token = security.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 form uses 'username' field -> we treat it as email
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    token = security.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=schemas.UserOut)
def me(current=Depends(security.get_current_user)):
    return current