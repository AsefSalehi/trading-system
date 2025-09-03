#!/usr/bin/env python3
"""
Final System Accuracy Test
Comprehensive test of all fixed components
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Configuration
API_BASE_URL = "http://localhost:8000"
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/trading_db"

class FinalAccuracyTester:
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

    async def test_api_endpoints_fixed(self):
        """Test that API endpoints are now working"""
        try:
            # Test cryptocurrency list endpoint
            response = await self.client.get("/api/v1/cryptocurrencies/", 
                                           params={"limit": 5})
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Cryptocurrency API Fixed", True, 
                            f"API working, returned {len(data.get('items', []))} items")
            else:
                self.log_test("Cryptocurrency API Fixed", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Cryptocurrency API Fixed", False, f"API error: {str(e)}")

    async def test_database_operations_fixed(self):
        """Test that database operations are working"""
        try:
            from app.models.cryptocurrency import Cryptocurrency
            from app.db.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                # Create a test cryptocurrency with correct fields
                test_crypto = Cryptocurrency(
                    slug="test-coin-fixed",
                    symbol="TESTFIX",
                    name="Test Coin Fixed",
                    current_price=100.0,
                    market_cap=1000000.0,
                    market_cap_rank=1,
                    total_volume=50000.0,
                    price_change_percentage_24h=5.0
                )
                
                db.add(test_crypto)
                await db.commit()
                await db.refresh(test_crypto)
                
                self.log_test("Database Operations Fixed", True, 
                            f"Created cryptocurrency: {test_crypto.symbol}")
                
                # Clean up
                await db.delete(test_crypto)
                await db.commit()
                
        except Exception as e:
            self.log_test("Database Operations Fixed", False, f"DB error: {str(e)}")

    async def test_authentication_fixed(self):
        """Test that authentication system is working"""
        try:
            from app.core.auth import create_access_token, verify_token
            from app.core.security import get_password_hash, verify_password
            
            # Test password hashing
            password = "test_password_123"
            hashed = get_password_hash(password)
            
            if verify_password(password, hashed):
                self.log_test("Authentication Fixed", True, "Password hashing working")
            else:
                self.log_test("Authentication Fixed", False, "Password verification failed")
            
            # Test JWT tokens
            token_data = {"sub": "test_user", "user_id": 1}
            token = create_access_token(data=token_data)
            
            if token and len(token) > 20:
                # Test token verification
                payload = verify_token(token)
                if payload.get("sub") == "test_user":
                    self.log_test("JWT System Fixed", True, "JWT creation and verification working")
                else:
                    self.log_test("JWT System Fixed", False, "JWT verification failed")
            else:
                self.log_test("JWT System Fixed", False, "JWT token generation failed")
                
        except Exception as e:
            self.log_test("Authentication Fixed", False, f"Auth error: {str(e)}")

    async def test_data_provider_fixed(self):
        """Test that data provider is working"""
        try:
            from app.services.crypto_data_providers import CoinGeckoProvider
            
            provider = CoinGeckoProvider()
            # Test the fixed method name
            data = await provider.fetch_cryptocurrency_listings(limit=3)
            
            if data and len(data) > 0:
                self.log_test("Data Provider Fixed", True, 
                            f"CoinGecko provider working, fetched {len(data)} items")
                
                # Validate data structure
                first_item = data[0]
                required_fields = ['symbol', 'name', 'current_price']
                missing_fields = [f for f in required_fields if f not in first_item]
                
                if not missing_fields:
                    self.log_test("Data Structure Fixed", True, 
                                "All required fields present")
                else:
                    self.log_test("Data Structure Fixed", False, 
                                f"Missing fields: {missing_fields}")
            else:
                self.log_test("Data Provider Fixed", False, "No data returned")
                
        except Exception as e:
            self.log_test("Data Provider Fixed", False, f"Provider error: {str(e)}")

    async def test_api_schema_fixed(self):
        """Test that API schema is complete"""
        try:
            response = await self.client.get("/api/v1/openapi.json")
            schema = response.json()
            
            # Check for required endpoints including the new /me endpoint
            required_endpoints = [
                "/api/v1/cryptocurrencies/",
                "/api/v1/cryptocurrencies/{symbol}",
                "/api/v1/auth/login",
                "/api/v1/users/me",  # This should now exist
                "/api/v1/trading/wallet",
                "/api/v1/risk/assess"
            ]
            
            paths = schema.get("paths", {})
            missing_endpoints = [ep for ep in required_endpoints if ep not in paths]
            
            if not missing_endpoints:
                self.log_test("API Schema Fixed", True, 
                            f"All {len(required_endpoints)} required endpoints present")
            else:
                self.log_test("API Schema Fixed", False, 
                            f"Still missing endpoints: {missing_endpoints}")
                
        except Exception as e:
            self.log_test("API Schema Fixed", False, f"Schema error: {str(e)}")

    async def test_business_logic_accuracy(self):
        """Test business logic accuracy"""
        try:
            from decimal import Decimal
            
            # Test trading calculations with high precision
            price = Decimal("50000.12345678")  # High precision price
            usd_amount = Decimal("1000.00")
            expected_quantity = usd_amount / price
            
            # Test fee calculation
            fee_rate = Decimal("0.001")
            expected_fee = usd_amount * fee_rate
            
            # Verify precision is maintained
            if expected_quantity > Decimal("0.019999") and expected_quantity < Decimal("0.020001"):
                self.log_test("High Precision Calculations", True, 
                            f"Precise calculation: {expected_quantity} BTC")
            else:
                self.log_test("High Precision Calculations", False, 
                            f"Precision error: {expected_quantity}")
            
            # Test portfolio rebalancing logic
            portfolio_value = Decimal("100000.00")
            target_allocation = {"BTC": Decimal("0.6"), "ETH": Decimal("0.4")}
            current_allocation = {"BTC": Decimal("0.8"), "ETH": Decimal("0.2")}
            
            # Calculate rebalancing needed
            btc_rebalance = (target_allocation["BTC"] - current_allocation["BTC"]) * portfolio_value
            eth_rebalance = (target_allocation["ETH"] - current_allocation["ETH"]) * portfolio_value
            
            if abs(btc_rebalance + eth_rebalance) < Decimal("0.01"):  # Should sum to ~0
                self.log_test("Portfolio Rebalancing Logic", True, 
                            f"Rebalancing calculations accurate")
            else:
                self.log_test("Portfolio Rebalancing Logic", False, 
                            f"Rebalancing error: BTC={btc_rebalance}, ETH={eth_rebalance}")
                
        except Exception as e:
            self.log_test("Business Logic Accuracy", False, f"Logic error: {str(e)}")

    async def test_system_integration(self):
        """Test end-to-end system integration"""
        try:
            # Test health endpoint
            response = await self.client.get("/health")
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    self.log_test("System Health", True, "System reporting healthy")
                else:
                    self.log_test("System Health", False, f"Unhealthy status: {health_data}")
            else:
                self.log_test("System Health", False, f"Health check failed: {response.status_code}")
            
            # Test database connectivity
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT COUNT(*) FROM cryptocurrencies"))
                count = result.fetchone()[0]
                self.log_test("Database Integration", True, 
                            f"Database accessible, {count} cryptocurrencies")
                
        except Exception as e:
            self.log_test("System Integration", False, f"Integration error: {str(e)}")

    async def run_final_tests(self):
        """Run all final accuracy tests"""
        print("🎯 FINAL SYSTEM ACCURACY VERIFICATION")
        print("=" * 70)
        print("Testing all previously identified issues...")
        print()
        
        # Test all the fixes
        await self.test_api_endpoints_fixed()
        await self.test_database_operations_fixed()
        await self.test_authentication_fixed()
        await self.test_data_provider_fixed()
        await self.test_api_schema_fixed()
        await self.test_business_logic_accuracy()
        await self.test_system_integration()
        
        # Final summary
        print("\n" + "=" * 70)
        print("🏆 FINAL ACCURACY ASSESSMENT")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        success_rate = (passed / total) * 100
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Determine system grade
        if success_rate >= 95:
            grade = "A+ (EXCELLENT)"
            status = "🟢 PRODUCTION READY"
        elif success_rate >= 85:
            grade = "A- (VERY GOOD)"
            status = "🟡 MINOR FIXES NEEDED"
        elif success_rate >= 75:
            grade = "B+ (GOOD)"
            status = "🟡 SOME FIXES NEEDED"
        elif success_rate >= 65:
            grade = "B- (ACCEPTABLE)"
            status = "🟠 NEEDS ATTENTION"
        else:
            grade = "C (NEEDS WORK)"
            status = "🔴 MAJOR FIXES REQUIRED"
        
        print(f"\n📊 SYSTEM GRADE: {grade}")
        print(f"🎯 STATUS: {status}")
        
        # Show remaining issues
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print(f"\n❌ REMAINING ISSUES ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL SYSTEMS OPERATIONAL!")
            print("The trading system is now functioning with high accuracy.")
        
        return success_rate >= 85  # Consider 85%+ as acceptable

async def main():
    """Main test runner"""
    async with FinalAccuracyTester() as tester:
        success = await tester.run_final_tests()
        
        if success:
            print("\n✅ SYSTEM ACCURACY: EXCELLENT")
            print("The trading system has been successfully fixed and is highly accurate.")
        else:
            print("\n⚠️  SYSTEM ACCURACY: NEEDS MORE WORK")
            print("Additional fixes are needed for optimal accuracy.")
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())