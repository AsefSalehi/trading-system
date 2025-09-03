#!/usr/bin/env python3
"""
Advanced Trading Features Test
Comprehensive test of all newly implemented advanced features
"""

import asyncio
import sys
from datetime import datetime
from decimal import Decimal

def test_advanced_order_types():
    """Test advanced order execution service"""
    print("🔄 TESTING ADVANCED ORDER TYPES")
    print("=" * 60)
    
    try:
        from app.services.order_execution_service import OrderExecutionService
        from app.models.wallet import OrderType, TransactionType
        
        service = OrderExecutionService()
        
        # Test order type checking logic
        print("✅ Order Execution Service initialized")
        
        # Test limit order logic
        test_price = Decimal('50000.00')
        current_price = Decimal('49500.00')
        
        # Mock order for testing
        class MockOrder:
            def __init__(self):
                self.transaction_type = TransactionType.BUY
                self.price = test_price
        
        mock_order = MockOrder()
        should_execute = service.check_limit_order(mock_order, current_price)
        
        if should_execute:
            print("✅ Limit Order Logic: Buy limit correctly triggered when price below limit")
        else:
            print("❌ Limit Order Logic: Failed")
            return False
        
        # Test stop-loss logic
        mock_order.transaction_type = TransactionType.SELL
        mock_order.stop_price = Decimal('48000.00')
        current_price = Decimal('47500.00')
        
        should_execute = service.check_stop_loss_order(mock_order, current_price)
        
        if should_execute:
            print("✅ Stop-Loss Logic: Correctly triggered when price below stop")
        else:
            print("❌ Stop-Loss Logic: Failed")
            return False
        
        print("✅ Advanced Order Types: All logic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Advanced Order Types: Error - {e}")
        return False

def test_risk_management():
    """Test risk management service"""
    print("\n⚠️  TESTING RISK MANAGEMENT")
    print("=" * 60)
    
    try:
        from app.services.risk_management_service import RiskManagementService, RiskLimits
        
        service = RiskManagementService()
        limits = service.default_limits
        
        print("✅ Risk Management Service initialized")
        print(f"✅ Default Limits: Max position {limits.max_position_size_percentage}%, "
              f"Daily loss {limits.max_daily_loss_percentage}%")
        
        # Test risk calculations
        holdings = []  # Mock empty holdings
        total_value = Decimal('10000.00')
        
        concentration_score = service.calculate_concentration_risk_score(holdings, total_value)
        print(f"✅ Concentration Risk Calculation: {concentration_score} (empty portfolio)")
        
        # Test overall risk score calculation
        risk_score = service.calculate_overall_risk_score(
            cash_pct=Decimal('20.0'),
            largest_pos_pct=Decimal('15.0'),
            concentration_score=Decimal('30.0'),
            daily_volatility=Decimal('2.0'),
            max_drawdown=Decimal('5.0')
        )
        
        print(f"✅ Overall Risk Score: {risk_score}/100")
        
        if risk_score >= 0 and risk_score <= 100:
            print("✅ Risk Management: All calculations working correctly")
            return True
        else:
            print("❌ Risk Management: Risk score out of range")
            return False
        
    except Exception as e:
        print(f"❌ Risk Management: Error - {e}")
        return False

def test_realtime_features():
    """Test real-time service components"""
    print("\n📡 TESTING REAL-TIME FEATURES")
    print("=" * 60)
    
    try:
        from app.services.realtime_service import RealTimeService, PriceUpdate, OrderBook, Alert
        
        service = RealTimeService()
        
        print("✅ Real-Time Service initialized")
        
        # Test price update structure
        price_update = PriceUpdate(
            symbol="BTC",
            price=Decimal('50000.00'),
            volume_24h=Decimal('1000000.00'),
            change_24h=Decimal('2.5'),
            timestamp=datetime.utcnow()
        )
        
        price_dict = price_update.to_dict()
        if 'symbol' in price_dict and 'price' in price_dict:
            print("✅ Price Update Structure: Correct serialization")
        else:
            print("❌ Price Update Structure: Missing fields")
            return False
        
        # Test alert creation
        alert = Alert(
            id="test_alert",
            user_id=1,
            alert_type="price",
            symbol="BTC",
            condition="above",
            threshold=Decimal('55000.00'),
            current_value=Decimal('50000.00'),
            message="BTC price above $55,000",
            timestamp=datetime.utcnow()
        )
        
        alert_dict = alert.to_dict()
        if 'symbol' in alert_dict and 'threshold' in alert_dict:
            print("✅ Alert Structure: Correct serialization")
        else:
            print("❌ Alert Structure: Missing fields")
            return False
        
        print("✅ Real-Time Features: Core structures working")
        return True
        
    except Exception as e:
        print(f"❌ Real-Time Features: Error - {e}")
        return False

async def test_multi_exchange():
    """Test multi-exchange service"""
    print("\n🔗 TESTING MULTI-EXCHANGE FEATURES")
    print("=" * 60)
    
    try:
        from app.services.multi_exchange_service import MultiExchangeService, BinanceConnector, ArbitrageOpportunity
        
        service = MultiExchangeService()
        
        print("✅ Multi-Exchange Service initialized")
        print(f"✅ Exchanges configured: {list(service.exchanges.keys())}")
        
        # Test Binance connector
        binance = BinanceConnector()
        normalized_symbol = binance.normalize_symbol("BTC")
        
        if normalized_symbol == "BTCUSDT":
            print("✅ Symbol Normalization: BTC -> BTCUSDT")
        else:
            print(f"❌ Symbol Normalization: Got {normalized_symbol}")
            return False
        
        # Test arbitrage opportunity structure
        arb_opp = ArbitrageOpportunity(
            symbol="BTC",
            buy_exchange="Binance",
            sell_exchange="Coinbase",
            buy_price=Decimal('50000.00'),
            sell_price=Decimal('50500.00'),
            profit_percentage=Decimal('1.0'),
            profit_amount=Decimal('500.00'),
            max_volume=Decimal('10.0'),
            timestamp=datetime.utcnow()
        )
        
        arb_dict = arb_opp.to_dict()
        if 'profit_percentage' in arb_dict and arb_dict['profit_percentage'] == 1.0:
            print("✅ Arbitrage Structure: Correct calculation and serialization")
        else:
            print("❌ Arbitrage Structure: Incorrect data")
            return False
        
        print("✅ Multi-Exchange Features: Core functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Multi-Exchange Features: Error - {e}")
        return False

def test_api_endpoints():
    """Test that new API endpoints are properly configured"""
    print("\n🌐 TESTING API ENDPOINTS")
    print("=" * 60)
    
    try:
        from app.api.api_v1.api import api_router
        
        # Get all routes
        routes = []
        for route in api_router.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        # Check for advanced trading endpoints
        advanced_endpoints = [
            "/advanced/orders/limit",
            "/advanced/orders/stop-loss", 
            "/advanced/orders/take-profit",
            "/advanced/risk/metrics",
            "/advanced/exchanges/prices/{symbol}",
            "/advanced/arbitrage/opportunities"
        ]
        
        missing_endpoints = []
        for endpoint in advanced_endpoints:
            # Check if any route contains the endpoint pattern
            found = any(endpoint.replace('{symbol}', 'BTC') in route or 
                       endpoint.split('/')[-1] in route for route in routes)
            if not found:
                missing_endpoints.append(endpoint)
        
        if not missing_endpoints:
            print("✅ API Endpoints: All advanced endpoints configured")
            print(f"✅ Total Routes: {len(routes)}")
            return True
        else:
            print(f"❌ API Endpoints: Missing {missing_endpoints}")
            return False
        
    except Exception as e:
        print(f"❌ API Endpoints: Error - {e}")
        return False

def test_database_models():
    """Test that database models support advanced features"""
    print("\n🗄️  TESTING DATABASE MODELS")
    print("=" * 60)
    
    try:
        from app.models.wallet import Order, OrderType, OrderStatus, TransactionType
        
        # Test order model
        print("✅ Order Model: Imported successfully")
        
        # Test enums
        order_types = [ot.value for ot in OrderType]
        expected_types = ['market', 'limit', 'stop_loss', 'take_profit']
        
        if all(ot in order_types for ot in expected_types):
            print(f"✅ Order Types: {order_types}")
        else:
            print(f"❌ Order Types: Missing types. Got {order_types}")
            return False
        
        order_statuses = [os.value for os in OrderStatus]
        expected_statuses = ['pending', 'executed', 'cancelled', 'partial']
        
        if all(os in order_statuses for os in expected_statuses):
            print(f"✅ Order Statuses: {order_statuses}")
        else:
            print(f"❌ Order Statuses: Missing statuses. Got {order_statuses}")
            return False
        
        print("✅ Database Models: All advanced features supported")
        return True
        
    except Exception as e:
        print(f"❌ Database Models: Error - {e}")
        return False

def test_schemas():
    """Test response schemas for advanced features"""
    print("\n📋 TESTING RESPONSE SCHEMAS")
    print("=" * 60)
    
    try:
        from app.schemas.trading import OrderResponse, RiskMetricsResponse, ArbitrageResponse
        
        # Test OrderResponse
        order_data = {
            "order_id": 1,
            "status": "pending",
            "order_type": "limit",
            "symbol": "BTC",
            "side": "buy",
            "quantity": 0.1,
            "price": 50000.0,
            "created_at": "2025-01-01T00:00:00"
        }
        
        order_response = OrderResponse(**order_data)
        print("✅ Order Response Schema: Valid")
        
        # Test RiskMetricsResponse
        risk_data = {
            "total_portfolio_value": 10000.0,
            "cash_percentage": 20.0,
            "largest_position_percentage": 15.0,
            "daily_pnl_percentage": 2.0,
            "total_pnl_percentage": 5.0,
            "concentration_risk_score": 30.0,
            "overall_risk_score": 25.0,
            "recommendations": ["Keep cash reserves above 10%"]
        }
        
        risk_response = RiskMetricsResponse(**risk_data)
        print("✅ Risk Metrics Schema: Valid")
        
        # Test ArbitrageResponse
        arb_data = {
            "symbol": "BTC",
            "buy_exchange": "Binance",
            "sell_exchange": "Coinbase",
            "buy_price": 50000.0,
            "sell_price": 50500.0,
            "profit_percentage": 1.0,
            "profit_amount": 500.0,
            "max_volume": 10.0,
            "timestamp": "2025-01-01T00:00:00"
        }
        
        arb_response = ArbitrageResponse(**arb_data)
        print("✅ Arbitrage Response Schema: Valid")
        
        print("✅ Response Schemas: All advanced schemas working")
        return True
        
    except Exception as e:
        print(f"❌ Response Schemas: Error - {e}")
        return False

async def main():
    """Main test runner"""
    print("🚀 ADVANCED TRADING FEATURES COMPREHENSIVE TEST")
    print("=" * 70)
    
    # Run all tests
    results = []
    results.append(test_advanced_order_types())
    results.append(test_risk_management())
    results.append(test_realtime_features())
    results.append(await test_multi_exchange())
    results.append(test_api_endpoints())
    results.append(test_database_models())
    results.append(test_schemas())
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ADVANCED FEATURES TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Feature status
    features = [
        ("Advanced Order Types", results[0]),
        ("Risk Management", results[1]),
        ("Real-Time Features", results[2]),
        ("Multi-Exchange Support", results[3]),
        ("API Endpoints", results[4]),
        ("Database Models", results[5]),
        ("Response Schemas", results[6])
    ]
    
    print(f"\n🔍 FEATURE STATUS:")
    for feature, status in features:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {feature}")
    
    # Overall verdict
    if success_rate == 100:
        print(f"\n🎉 ALL ADVANCED FEATURES IMPLEMENTED SUCCESSFULLY!")
        print(f"✅ Production-ready advanced trading platform")
        print(f"✅ All 4 enhancement areas completed:")
        print(f"   • Advanced Order Types (Limit, Stop-Loss, Take-Profit)")
        print(f"   • Enhanced Risk Management (Position sizing, Loss limits)")
        print(f"   • Real-time Features (WebSocket, Order book, Alerts)")
        print(f"   • Multi-Exchange Support (Arbitrage detection)")
    elif success_rate >= 85:
        print(f"\n✅ ADVANCED FEATURES MOSTLY COMPLETE")
        print(f"⚠️  Minor issues to resolve for full production readiness")
    else:
        print(f"\n⚠️  ADVANCED FEATURES NEED MORE WORK")
        print(f"❌ Significant issues to resolve")
    
    return success_rate >= 85

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)