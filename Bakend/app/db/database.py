from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL, echo=True, future=True  # Set to False in production
)

# Create sync engine for auth (convert asyncpg URL to psycopg2)
sync_database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(sync_database_url, echo=True)

# Create session factories
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Create declarative base
Base = declarative_base()


async def get_db():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Dependency to get sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
