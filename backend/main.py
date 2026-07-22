from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.database.db import Base, engine, SessionLocal
from backend.database.models import User
from backend.auth.security import hash_password
from backend.utils.config import settings
from backend.utils.limiter import limiter
from backend.auth.routes import router as auth_router
from backend.api.scan_routes import router as scan_router
from backend.api.admin_routes import router as admin_router
from backend.api.saved_routes import router as saved_router
from backend.reports.report_routes import router as report_router

Base.metadata.create_all(bind=engine)


def seed_default_users():
    """Creates a demo admin + analyst login. Only ever runs when
    SEED_DEFAULT_USERS=True is explicitly set (see utils/config.py), which
    is blocked outright when ENVIRONMENT=production. Never let this run
    unguarded again - it's how the site would ship with a public admin
    login of admin@cyberinspect.io / admin123."""
    db = SessionLocal()
    try:
        defaults = [
            ("Admin", "admin@cyberinspect.io", "admin123", "admin"),
            ("Demo User", "user@demo.io", "user123", "analyst"),
        ]
        for name, email, password, role in defaults:
            if not db.query(User).filter(User.email == email).first():
                db.add(User(name=name, email=email,
                            hashed_password=hash_password(password), role=role))
        db.commit()
    finally:
        db.close()


if settings.SEED_DEFAULT_USERS:
    seed_default_users()

app = FastAPI(title=settings.APP_NAME,
              description="Website Security Assessment Platform API",
              version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(report_router)
app.include_router(admin_router)
app.include_router(saved_router)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": "/docs"}