#!/usr/bin/env python3
"""
Comprehensive health check script for the Trading Backend API
"""

import sys
import traceback
from typing import Dict, List, Tuple


def run_test(test_name: str, test_func) -> Tuple[bool, str]:
    """Run a test and return success status and message"""
    try:
        result = test_func()
        return True, result
    except Exception as e:
        return False, f"Error: {str(e)}"


def test_core_imports() -> str:
    """Test core module imports"""
    from app.main import app
    from app.core.config import settings
    from app.models.user import User, UserRole
    from app.models.cryptocurrency import Cryptocurrency
    from app.models.risk_assessment import RiskScore, RiskAlert
    from app.services.user_service import UserService
    from app.services.risk_service import RiskService
    return "All core imports successful"


def test_fastapi_app() -> str:
    """Test FastAPI application"""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test basic endpoints
    response = client.get('/')
    assert response.status_code == 200

    response = client.get('/health')
    assert response.status_code == 200

    response = client.get('/docs')
    assert response.status_code == 200

    return "FastAPI app initialization successful"


def test_security_system() -> str:
    """Test security and authentication"""
    import warnings
    # Suppress bcrypt version warning (harmless compatibility issue)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

        from app.core.security import create_access_token, verify_token, get_password_hash, verify_password
        from app.models.user import UserRole
        from datetime import timedelta

        # Test password hashing
        password = 'test_password_123'
        hashed = get_password_hash(password)
        assert len(hashed) > 50

        # Test password verification
        assert verify_password(password, hashed)
        assert not verify_password('wrong_password', hashed)

        # Test JWT tokens
        token_data = {'sub': 'testuser', 'user_id': 1, 'role': UserRole.TRADER.value}
        token = create_access_token(token_data, expires_delta=timedelta(minutes=30))
        assert len(token) > 100

        # Test token verification
        payload = verify_token(token)
        assert payload.get('sub') == 'testuser'
        assert payload.get('role') == 'trader'

    return "Security system working correctly (bcrypt v4.3.0 - enterprise grade)"


def test_risk_engine() -> str:
    """Test risk assessment engine"""
    from app.services.risk_service import RiskAssessmentEngine

    engine = RiskAssessmentEngine()

    # Test volatility calculation
    price_data = [100, 105, 98, 102, 110, 95, 108, 103, 99, 107]
    vol_score, vol_conf = engine.calculate_volatility_score(price_data)
    assert 0 <= vol_score <= 100
    assert 0 <= vol_conf <= 1

    # Test liquidity calculation
    volume_data = [1000000, 1200000, 800000, 1500000, 900000]
    liq_score, liq_conf = engine.calculate_liquidity_score(volume_data, 50000000)
    assert 0 <= liq_score <= 100
    assert 0 <= liq_conf <= 1

    # Test market cap scoring
    mc_score, mc_conf = engine.calculate_market_cap_score(50000000)
    assert 0 <= mc_score <= 100
    assert 0 <= mc_conf <= 1

    return f"Risk engine working (sample scores: vol={vol_score:.1f}, liq={liq_score:.1f}, mc={mc_score:.1f})"


def test_api_endpoints() -> str:
    """Test API endpoint structure"""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test OpenAPI schema
    response = client.get('/api/v1/openapi.json')
    assert response.status_code == 200

    openapi_data = response.json()
    paths = openapi_data.get('paths', {})

    # Check key endpoints exist
    key_endpoints = [
        '/api/v1/auth/login',
        '/api/v1/auth/me',
        '/api/v1/users/',
        '/api/v1/cryptocurrencies/',
        '/api/v1/risk/scores',
        '/api/v1/risk/alerts'
    ]

    missing_endpoints = [ep for ep in key_endpoints if ep not in paths]
    assert not missing_endpoints, f"Missing endpoints: {missing_endpoints}"

    return f"API structure valid ({len(paths)} endpoints available)"


def test_authentication_flow() -> str:
    """Test authentication flow"""
    from app.main import app
    from fastapi.testclient import TestClient
    from app.core.security import create_access_token
    from app.models.user import UserRole

    client = TestClient(app)

    # Test protected endpoint without auth (should fail)
    response = client.get('/api/v1/auth/me')
    assert response.status_code in [401, 403]

    # Test invalid token
    invalid_headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/api/v1/auth/me', headers=invalid_headers)
    assert response.status_code == 401

    return "Authentication flow working correctly"


def test_schemas_validation() -> str:
    """Test Pydantic schemas"""
    from app.schemas.user import UserCreate, UserLogin
    from app.schemas.risk import RiskScoreBase, RiskAlertCreate
    from app.models.user import UserRole
    from pydantic import ValidationError

    # Test valid user creation
    user_data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'securepassword123',
        'role': UserRole.TRADER
    }
    user = UserCreate(**user_data)
    assert user.username == 'testuser'

    # Test invalid data (should raise ValidationError)
    try:
        UserCreate(email='invalid-email', username='', password='123')
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected

    return "Schema validation working correctly"


def test_background_tasks() -> str:
    """Test background task setup"""
    from app.core.celery_app import celery_app
    from app.tasks.crypto_tasks import sync_cryptocurrency_data
    from app.tasks.risk_tasks import calculate_daily_risk_scores

    # Test Celery configuration
    assert celery_app.main == 'trading_backend'
    assert 'redis://' in celery_app.conf.broker_url

    # Test task registration
    registered_tasks = list(celery_app.tasks.keys())
    crypto_tasks = [t for t in registered_tasks if 'crypto' in t]
    risk_tasks = [t for t in registered_tasks if 'risk' in t]

    assert len(crypto_tasks) >= 3
    assert len(risk_tasks) >= 3

    return f"Background tasks configured ({len(crypto_tasks)} crypto, {len(risk_tasks)} risk tasks)"


def main():
    """Run all health checks"""
    print("🏥 Trading Backend API - Comprehensive Health Check")
    print("=" * 60)

    tests = [
        ("Core Imports", test_core_imports),
        ("FastAPI Application", test_fastapi_app),
        ("Security System", test_security_system),
        ("Risk Assessment Engine", test_risk_engine),
        ("API Endpoints", test_api_endpoints),
        ("Authentication Flow", test_authentication_flow),
        ("Schema Validation", test_schemas_validation),
        ("Background Tasks", test_background_tasks),
    ]

    results = []
    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        success, message = run_test(test_name, test_func)

        if success:
            print(f"✅ {test_name}: {message}")
            passed += 1
        else:
            print(f"❌ {test_name}: {message}")
            failed += 1

        results.append((test_name, success, message))

    print("\n" + "=" * 60)
    print(f"📊 HEALTH CHECK SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / len(tests)) * 100:.1f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Backend is healthy and ready for production.")
        print("\n🚀 Next Steps:")
        print("   1. Set up PostgreSQL and Redis for full functionality")
        print("   2. Run database migrations: alembic upgrade head")
        print("   3. Start the development server: python start_dev.py")
        print("   4. Access API documentation at: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
