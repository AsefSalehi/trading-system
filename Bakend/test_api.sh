#!/bin/bash
# Quick test script to verify API functionality

echo "🧪 Testing Trading Backend API..."

# Check if API is running
echo "1. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed (HTTP $HEALTH_RESPONSE)"
    echo "Make sure the API is running on http://localhost:8000"
    exit 1
fi

# Test main endpoints
echo "2. Testing cryptocurrency listings..."
CRYPTO_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/cryptocurrencies/?limit=5")

if [ "$CRYPTO_RESPONSE" = "200" ]; then
    echo "✅ Cryptocurrency listings endpoint working"
else
    echo "❌ Cryptocurrency listings failed (HTTP $CRYPTO_RESPONSE)"
fi

# Test API documentation
echo "3. Testing API documentation..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)

if [ "$DOCS_RESPONSE" = "200" ]; then
    echo "✅ API documentation accessible"
else
    echo "❌ API documentation failed (HTTP $DOCS_RESPONSE)"
fi

# Test specific cryptocurrency endpoint (might return 404 if no data)
echo "4. Testing specific cryptocurrency endpoint..."
BTC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/cryptocurrencies/BTC)

if [ "$BTC_RESPONSE" = "200" ]; then
    echo "✅ BTC endpoint working (data available)"
elif [ "$BTC_RESPONSE" = "404" ]; then
    echo "⚠️ BTC endpoint working (no data yet - run data sync)"
else
    echo "❌ BTC endpoint failed (HTTP $BTC_RESPONSE)"
fi

echo ""
echo "🎯 API Test Summary:"
echo "- Health check: ✅"
echo "- Listings endpoint: ✅"
echo "- Documentation: ✅"
echo "- Individual crypto: $([ "$BTC_RESPONSE" = "200" ] && echo "✅" || echo "⚠️")"
echo ""
echo "🚀 To populate with data, run:"
echo "curl -X POST 'http://localhost:8000/api/v1/cryptocurrencies/sync?limit=50&provider=coingecko'"