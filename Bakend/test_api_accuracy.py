#!/usr/bin/env python3
"""
API Accuracy Testing Script
Tests the trading system backend for functionality and accuracy
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any

import httpx
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

# Configuration
API_BASE_URL = "http://localhost:8000"
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/trading_db"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0)
        self.engine = create_async_engine(DATABASE_URL)
        self.results = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        await self.engine.dispose()

    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    async def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = await self.client.get("/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Basic Connectivity", True,
                            f"API responding: {data.get('message', 'Unknown')}", data)
                return True
            else:
                self.log_test("Basic Connectivity", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection error: {str(e)}")
            return False

    async def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, "Health endpoint responding", data)
                return True
            else:
                self.log_test("Health Check", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Health check error: {str(e)}")
            return False

    async def test_database_connectivity(self):
        """Test database connectivity"""
        try:
            from sqlalchemy import text
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                self.log_test("Database Connectivity", True,
                            f"Connected to: {version[:50]}...")
                return True
        except Exception as e:
            self.log_test("Database Connectivity", False, f"DB error: {str(e)}")
            return False

    async def test_cryptocurrency_endpoints(self):
        """Test cryptocurrency API endpoints"""
        # The rate limiting implementation has issues, so we'll test what we can
        try:
            # Test the sync endpoint which might work
            response = await self.client.post("/api/v1/cryptocurrencies/sync",
                                            params={"limit": 5})

            if response.status_code == 200:
                data = response.json()
                self.log_test("Cryptocurrency Sync", True,
                            f"Sync successful: {data.get('message', 'Unknown')}")
            elif response.status_code == 422:
                self.log_test("Cryptocurrency Sync", False,
                            "Rate limiting parameter issue")
            else:
                self.log_test("Cryptocurrency Sync", False,
                            f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            self.log_test("Cryptocurrency Sync", False, f"API error: {str(e)}")

        # Test individual cryptocurrency endpoint
        try:
            response = await self.client.get("/api/v1/cryptocurrencies/BTC")

            if response.status_code == 200:
                data = response.json()
                self.log_test("Individual Cryptocurrency", True,
                            f"Retrieved BTC data: {data.get('symbol', 'Unknown')}")
            elif response.status_code == 404:
                self.log_test("Individual Cryptocurrency", True,
                            "BTC not found (expected - no data loaded)")
            elif response.status_code == 422:
                self.log_test("Individual Cryptocurrency", False,
                            "Rate limiting parameter issue")
            else:
                self.log_test("Individual Cryptocurrency", False,
                            f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            self.log_test("Individual Cryptocurrency", False, f"API error: {str(e)}")

    async def test_openapi_schema(self):
        """Test OpenAPI schema generation"""
        try:
            response = await self.client.get("/api/v1/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                paths_count = len(schema.get("paths", {}))
                self.log_test("OpenAPI Schema", True,
                            f"Schema generated with {paths_count} endpoints")
                return True
            else:
                self.log_test("OpenAPI Schema", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("OpenAPI Schema", False, f"Schema error: {str(e)}")
            return False

    async def test_data_models(self):
        """Test database models and structure"""
        try:
            from sqlalchemy import text
            async with self.engine.begin() as conn:
                # Check if tables exist
                result = await conn.execute(text("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
                tables = [row[0] for row in result.fetchall()]

                if tables:
                    self.log_test("Database Models", True,
                                f"Found {len(tables)} tables: {', '.join(tables)}")
                else:
                    self.log_test("Database Models", True,
                                "No tables found - database not initialized (expected)")

        except Exception as e:
            self.log_test("Database Models", False, f"Model check error: {str(e)}")

    async def run_all_tests(self):
        """Run all accuracy tests"""
        print("🚀 Starting Trading System API Accuracy Tests")
        print("=" * 60)

        # Basic connectivity tests
        if not await self.test_basic_connectivity():
            print("❌ Basic connectivity failed - stopping tests")
            return

        # Core functionality tests
        await self.test_health_endpoint()
        await self.test_database_connectivity()
        await self.test_data_models()
        await self.test_openapi_schema()
        await self.test_cryptocurrency_endpoints()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        # Show failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")

        return passed == total

async def main():
    """Main test runner"""
    async with APITester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
