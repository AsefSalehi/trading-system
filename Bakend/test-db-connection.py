#!/usr/bin/env python3
"""Test database connection script"""

import os
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

async def test_connection():
    """Test database connection"""
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/trading_db")
    
    print(f"Testing connection to: {database_url}")
    
    try:
        # Test with SQLAlchemy
        engine = create_async_engine(database_url)
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ SQLAlchemy connection successful!")
        await engine.dispose()
        
        # Test with asyncpg directly
        # Extract connection params from URL
        url_parts = database_url.replace("postgresql+asyncpg://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        host_port = host_db[0].split(":")
        
        conn = await asyncpg.connect(
            user=user_pass[0],
            password=user_pass[1],
            host=host_port[0],
            port=int(host_port[1]),
            database=host_db[1]
        )
        
        result = await conn.fetchval("SELECT 1")
        print("✅ Direct asyncpg connection successful!")
        await conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)