from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User
from backend.utils.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(pw: str) -> str:
    # bcrypt only ever uses the first 72 bytes of the input; truncate
    # explicitly so a long password gets bcrypt-truncated rather than
    # raising ValueError.
    pw_bytes = pw.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise cred_exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise cred_exc
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user