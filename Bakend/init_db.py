#!/usr/bin/env python3
"""
Database Initialization Script
Creates all tables and sets up the database schema
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.database import Base

# Import all models to ensure they're registered
from app.models.cryptocurrency import Cryptocurrency, PriceHistory
from app.models.user import User
from app.models.wallet import Wallet, Transaction, Holding
from app.models.risk_assessment import RiskScore, RiskAlert
from app.models.portfolio import Portfolio

async def init_database():
    """Initialize database with all tables"""
    print("🔧 Initializing database...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Drop all tables (for clean setup)
            print("Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
            # Create all tables
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Database initialized successfully!")
        
        # Verify tables were created
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())