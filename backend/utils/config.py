import sys
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CyberInspect"
    ENVIRONMENT: str = "production"          # "development" or "production"
    DATABASE_URL: str                        # no insecure fallback default
    JWT_SECRET: str                          # no insecure fallback default
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:5500"]
    SEED_DEFAULT_USERS: bool = False         # only ever True in local dev
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

if "CHANGE_THIS" in settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
    sys.exit(
        "FATAL: JWT_SECRET is missing, too short, or a placeholder.\n"
        "Generate one: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
if "*" in settings.CORS_ORIGINS:
    sys.exit("FATAL: CORS_ORIGINS must not contain '*' while allow_credentials=True.")
if settings.ENVIRONMENT == "production" and settings.SEED_DEFAULT_USERS:
    sys.exit("FATAL: SEED_DEFAULT_USERS must be False in production.")
