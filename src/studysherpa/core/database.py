from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from studysherpa.core.config import settings

engine = create_async_engine(settings.database_url, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=True)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
