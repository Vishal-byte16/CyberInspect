import sys

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CyberInspect"


    ENVIRONMENT: str = "production"

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours


    CORS_ORIGINS: list[str] = ["https://cyber-inspect.netlify.app/","http://localhost:3000", "http://127.0.0.1:5500"]

    SEED_DEFAULT_USERS: bool = False

    class Config:
        env_file = ".env"


settings = Settings()


if "CHANGE_THIS" in settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
    sys.exit(
        "FATAL: JWT_SECRET is missing, too short, or still set to a placeholder value.\n"
        "Generate a real secret and put it in your .env file, e.g.:\n"
        "    openssl rand -hex 32\n"
        "JWT_SECRET=<paste the generated value here>"
    )

if settings.ENVIRONMENT == "production" and settings.SEED_DEFAULT_USERS:
    sys.exit(
        "FATAL: SEED_DEFAULT_USERS is enabled while ENVIRONMENT=production.\n"
        "This would create a well-known admin/demo login on your live site. "
        "Set SEED_DEFAULT_USERS=False (or unset it) before deploying."
    )