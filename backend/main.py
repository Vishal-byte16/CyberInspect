from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import Base, engine
from backend.utils.config import settings
from backend.auth.routes import router as auth_router
from backend.api.scan_routes import router as scan_router
from backend.api.admin_routes import router as admin_router
from backend.reports.report_routes import router as report_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME,
              description="Website Security Assessment Platform API",
              version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(report_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": "/docs"}