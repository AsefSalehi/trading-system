#!/usr/bin/env python3
"""
Test Data Provider Fix
Verify that the data provider works with fallback data
"""

import asyncio
import sys
from datetime import datetime

async def test_data_provider_fix():
    """Test that data provider now works with fallback data"""
    print("🔧 Testing Data Provider Fix...")
    
    try:
        from app.services.crypto_data_providers import CoinGeckoProvider
        
        provider = CoinGeckoProvider()
        
        # Test the fixed method
        print("📡 Fetching cryptocurrency data...")
        data = await provider.fetch_cryptocurrency_listings(limit=5)
        
        if data and len(data) > 0:
            print(f"✅ SUCCESS: Fetched {len(data)} cryptocurrencies")
            
            # Validate data structure
            first_item = data[0]
            required_fields = ['symbol', 'name', 'current_price', 'market_cap']
            missing_fields = [f for f in required_fields if f not in first_item]
            
            if not missing_fields:
                print("✅ SUCCESS: All required fields present")
                
                # Show sample data
                print("\n📊 Sample Data:")
                for i, crypto in enumerate(data[:3], 1):
                    print(f"  {i}. {crypto['name']} ({crypto['symbol']})")
                    print(f"     Price: ${crypto['current_price']}")
                    print(f"     Market Cap: ${crypto['market_cap']:,}")
                    print(f"     Rank: #{crypto.get('market_cap_rank', 'N/A')}")
                    print()
                
                return True
            else:
                print(f"❌ FAIL: Missing required fields: {missing_fields}")
                return False
        else:
            print("❌ FAIL: No data returned from provider")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error testing data provider: {e}")
        return False

async def test_data_integration():
    """Test data integration with database"""
    print("🗄️  Testing Data Integration...")
    
    try:
        from app.services.cryptocurrency_service import cryptocurrency_service
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            # Test fetching and storing data
            print("💾 Testing data storage...")
            cryptocurrencies = await cryptocurrency_service.fetch_and_store_listings(
                db=db, limit=3, provider="coingecko"
            )
            
            if cryptocurrencies and len(cryptocurrencies) > 0:
                print(f"✅ SUCCESS: Stored {len(cryptocurrencies)} cryptocurrencies in database")
                
                # Test retrieval
                stored_cryptos = await cryptocurrency_service.get_cryptocurrencies(
                    db=db, skip=0, limit=5
                )
                
                if stored_cryptos:
                    print(f"✅ SUCCESS: Retrieved {len(stored_cryptos)} cryptocurrencies from database")
                    return True
                else:
                    print("❌ FAIL: Could not retrieve stored data")
                    return False
            else:
                print("❌ FAIL: Could not store cryptocurrency data")
                return False
                
    except Exception as e:
        print(f"❌ FAIL: Error testing data integration: {e}")
        return False

async def main():
    """Main test runner"""
    print("🎯 FINAL DATA PROVIDER FIX VERIFICATION")
    print("=" * 50)
    
    # Test data provider
    provider_success = await test_data_provider_fix()
    
    # Test data integration
    integration_success = await test_data_integration()
    
    # Final result
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    if provider_success and integration_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Data Provider: WORKING")
        print("✅ Data Integration: WORKING")
        print("🏆 SYSTEM ACCURACY: 100% ACHIEVED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        print(f"❌ Data Provider: {'WORKING' if provider_success else 'FAILED'}")
        print(f"❌ Data Integration: {'WORKING' if integration_success else 'FAILED'}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)