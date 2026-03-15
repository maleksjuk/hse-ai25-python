import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from uuid import uuid4
from src.main import app
from src.db.models import Base


@pytest.fixture(autouse=True)
def init_cache():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    FastAPICache.reset()


@pytest.fixture
def mock_user():
    user_id = uuid4()
    user = type('User', (), {
        'id': user_id,
        'email': 'test@example.com',
        'is_active': True
    })()
    return user


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    async_session_maker = sessionmaker( async_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
        await session.close()
