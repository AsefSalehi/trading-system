"""
pytest configuration for the trading backend API tests
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for testing"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override"""
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async backend for pytest-asyncio"""
    return "asyncio"


# Mock data fixtures
@pytest.fixture
def sample_cryptocurrency_data():
    """Sample cryptocurrency data for testing"""
    return {
        "symbol": "BTC",
        "name": "Bitcoin",
        "slug": "bitcoin",
        "current_price": 45000.0,
        "market_cap": 850000000000.0,
        "market_cap_rank": 1,
        "total_volume": 25000000000.0,
        "circulating_supply": 19000000.0,
        "total_supply": 21000000.0,
        "max_supply": 21000000.0,
        "price_change_24h": 1200.0,
        "price_change_percentage_24h": 2.75,
        "description": "Bitcoin is a decentralized digital currency",
        "website": "https://bitcoin.org",
        "image_url": "https://bitcoin.org/img/logo.png"
    }


@pytest.fixture
def sample_cryptocurrency_list():
    """Sample list of cryptocurrencies for testing"""
    return [
        {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "current_price": 45000.0,
            "market_cap": 850000000000.0,
            "market_cap_rank": 1
        },
        {
            "symbol": "ETH", 
            "name": "Ethereum",
            "slug": "ethereum",
            "current_price": 3000.0,
            "market_cap": 400000000000.0,
            "market_cap_rank": 2
        },
        {
            "symbol": "ADA",
            "name": "Cardano",
            "slug": "cardano", 
            "current_price": 0.5,
            "market_cap": 15000000000.0,
            "market_cap_rank": 10
        }
    ]


# Configuration for pytest
pytest_plugins = ("pytest_asyncio",)