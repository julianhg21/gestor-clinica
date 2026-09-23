from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql://duality:duality_dev_password@localhost:5432/duality")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-only-secret-change-me-please-123456789")
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", "480"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",") if origin.strip()
    )


settings = Settings()
