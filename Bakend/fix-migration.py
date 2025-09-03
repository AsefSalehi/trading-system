#!/usr/bin/env python3
"""
Fix migration script to handle enum conflicts
"""
import os
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_migration():
    """Fix the migration by handling enum conflicts"""
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/trading_db")
    
    print(f"Connecting to database: {database_url}")
    
    try:
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
        
        print("✅ Connected to database")
        
        # Check if enum exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'userrole'
            )
        """)
        
        if result:
            print("⚠️ UserRole enum already exists, dropping it...")
            await conn.execute("DROP TYPE IF EXISTS userrole CASCADE")
            print("✅ Dropped existing enum")
        
        # Check if users table exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """)
        
        if result:
            print("⚠️ Users table already exists, dropping it...")
            await conn.execute("DROP TABLE IF EXISTS users CASCADE")
            print("✅ Dropped existing users table")
        
        # Check if alembic version table exists and clear it
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            )
        """)
        
        if result:
            print("🔄 Clearing alembic version history...")
            await conn.execute("DELETE FROM alembic_version")
            print("✅ Cleared migration history")
        
        await conn.close()
        print("✅ Database prepared for fresh migration")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_migration())
    exit(0 if success else 1)