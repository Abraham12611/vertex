from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@postgres:5432/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
