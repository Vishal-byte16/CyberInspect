from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CyberInspect"
    DATABASE_URL: str = "postgresql://postgres:postgres245@localhost:5432/CyberInspect"
    JWT_SECRET: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:5500", "*"]

    class Config:
        env_file = ".env"

settings = Settings()