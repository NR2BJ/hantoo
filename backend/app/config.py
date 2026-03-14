from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Minimal infrastructure config - only what's needed to connect to DB/Redis.
    All other settings (JWT, encryption, KIS, LLM, etc.) are stored in the
    database and managed via the web UI setup wizard / admin settings page.
    """

    DATABASE_URL: str = "postgresql+asyncpg://hantoo:password@postgres:5432/hantoo"
    REDIS_URL: str = "redis://redis:6379/0"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
