from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://hantoo:password@localhost:5432/hantoo"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Encryption for KIS credentials
    ENCRYPTION_KEY: str = ""

    # KIS API
    KIS_PROD_BASE_URL: str = "https://openapi.koreainvestment.com:9443"
    KIS_PAPER_BASE_URL: str = "https://openapivts.koreainvestment.com:29443"
    KIS_WS_URL: str = "ws://ops.koreainvestment.com:21000"
    KIS_WSS_URL: str = "wss://ops.koreainvestment.com:21000"

    # LLM
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "claude"

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
