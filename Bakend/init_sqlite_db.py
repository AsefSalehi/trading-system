#!/usr/bin/env python3
"""
Simple SQLite database initialization script
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.database import Base
from app.core.config import settings

# Import all models to register them with Base
from app.models.user import User
from app.models.cryptocurrency import Cryptocurrency, PriceHistory
from app.models.wallet import Wallet, Transaction, Holding, Order
from app.models.risk_assessment import RiskScore, RiskAlert

async def init_database():
    """Initialize SQLite database with all tables"""
    print("🔧 Initializing SQLite database...")

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
    )

    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Database initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
