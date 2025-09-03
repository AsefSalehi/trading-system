#!/usr/bin/env python3
"""
Test Error Fixes
Verify that bcrypt and logging errors are resolved
"""

import asyncio
import sys
from datetime import datetime

def test_bcrypt_fix():
    """Test that bcrypt version error is fixed"""
    print("🔐 Testing BCrypt Fix...")
    
    try:
        from app.core.security import get_password_hash, verify_password
        
        # Test password hashing without version errors
        test_password = "test_password_123"
        hashed = get_password_hash(test_password)
        
        if hashed and len(hashed) > 20:
            print("✅ BCrypt hashing working")
            
            # Test password verification
            if verify_password(test_password, hashed):
                print("✅ BCrypt verification working")
                return True
            else:
                print("❌ BCrypt verification failed")
                return False
        else:
            print("❌ BCrypt hashing failed")
            return False
            
    except Exception as e:
        print(f"❌ BCrypt error: {e}")
        return False

def test_logging_fix():
    """Test that logging correlation_id error is fixed"""
    print("📝 Testing Logging Fix...")
    
    try:
        from app.core.logging import logger
        
        # Test logging without correlation ID (should not error)
        logger.info("Test message without correlation ID")
        print("✅ Logging without correlation ID working")
        
        # Test logging with correlation ID
        corr_id = logger.set_correlation_id("test-123")
        logger.info("Test message with correlation ID")
        print(f"✅ Logging with correlation ID working: {corr_id}")
        
        # Test various log levels
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")
        print("✅ All log levels working")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging error: {e}")
        return False

async def test_data_provider_no_errors():
    """Test that data provider works without errors"""
    print("📡 Testing Data Provider (No Errors)...")
    
    try:
        from app.services.crypto_data_providers import CoinGeckoProvider
        
        provider = CoinGeckoProvider()
        data = await provider.fetch_cryptocurrency_listings(limit=2)
        
        if data and len(data) > 0:
            print(f"✅ Data provider working: {len(data)} items fetched")
            return True
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Data provider error: {e}")
        return False

def test_authentication_no_errors():
    """Test that authentication works without errors"""
    print("🔑 Testing Authentication (No Errors)...")
    
    try:
        from app.core.auth import create_access_token, verify_token
        
        # Test JWT token creation
        token_data = {"sub": "test_user", "user_id": 1}
        token = create_access_token(data=token_data)
        
        if token and len(token) > 20:
            print("✅ JWT token creation working")
            
            # Test token verification
            payload = verify_token(token)
            if payload.get("sub") == "test_user":
                print("✅ JWT token verification working")
                return True
            else:
                print("❌ JWT verification failed")
                return False
        else:
            print("❌ JWT token creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

async def main():
    """Main test runner"""
    print("🔧 TESTING ERROR FIXES")
    print("=" * 50)
    
    # Test all fixes
    bcrypt_success = test_bcrypt_fix()
    logging_success = test_logging_fix()
    data_success = await test_data_provider_no_errors()
    auth_success = test_authentication_no_errors()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ERROR FIX RESULTS")
    print("=" * 50)
    
    total_tests = 4
    passed_tests = sum([bcrypt_success, logging_success, data_success, auth_success])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Individual results
    print(f"\n🔐 BCrypt Fix: {'✅ WORKING' if bcrypt_success else '❌ FAILED'}")
    print(f"📝 Logging Fix: {'✅ WORKING' if logging_success else '❌ FAILED'}")
    print(f"📡 Data Provider: {'✅ WORKING' if data_success else '❌ FAILED'}")
    print(f"🔑 Authentication: {'✅ WORKING' if auth_success else '❌ FAILED'}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL ERROR FIXES SUCCESSFUL!")
        print("✅ System is now error-free and stable")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} ERROR(S) STILL PRESENT")
        print("❌ Additional fixes needed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)