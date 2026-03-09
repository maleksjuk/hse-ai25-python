from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DB_TYPE = AsyncSession
USE_ASYNC_VERSION = True

if USE_ASYNC_VERSION:
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_async_engine(DATABASE_URL)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

else:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL)
    session_maker = sessionmaker(bind=engine)

    def get_session() -> Generator[Session, None, None]:
        with session_maker() as session:
            yield session

