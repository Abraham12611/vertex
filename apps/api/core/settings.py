from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_SSLMODE: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET: str = "dummy"  # Provide a default for Alembic if not needed

    # Groq API
    GROQ_API_KEY: str

    # Coral Protocol
    CORAL_SERVER_URL: str = "http://localhost:8001"
    CORAL_API_KEY: str = ""

    # Moz API (SEO)
    MOZ_API_KEY: str = ""
    MOZ_SECRET_KEY: str = ""

    # Vector Search
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"

    # App Settings
    DEBUG: bool = True
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
