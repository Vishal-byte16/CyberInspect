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

# Auto-run the finding-fields migration on every startup. Safe to run
# repeatedly (uses ADD COLUMN IF NOT EXISTS) - needed because Render's free
# tier has no shell access to run one-off migration scripts manually.
try:
    with engine.begin() as conn:
        for col, coltype in {
            "confidence": "VARCHAR DEFAULT 'high'",
            "impact": "TEXT",
            "recommendation": "TEXT",
            "evidence": "TEXT",
            "owasp": "VARCHAR",
            "cwe": "VARCHAR",
        }.items():
            conn.exec_driver_sql(
                f"ALTER TABLE security_findings ADD COLUMN IF NOT EXISTS {col} {coltype}"
            )
except Exception as e:
    print(f"Migration warning (safe to ignore if columns already exist): {e}")


def seed_default_users():
    """Only runs when SEED_DEFAULT_USERS=True (blocked outright in production
    by config.py). Creates the demo admin/analyst logins for local testing."""
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

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": "/docs"}
