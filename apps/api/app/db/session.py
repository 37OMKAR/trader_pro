"""
Market AI — Database Session & Initialization
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from apps.api.app.core.config import settings
from apps.api.app.db.models import Base

# Async engine for PostgreSQL or SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initializes all database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing database sessions to FastAPI routes."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
