#!/bin/bash

# Trading System Docker Startup Script
echo "🚀 Starting Trading System with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update the configuration."
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U user -d trading_db > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Check API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is ready"
else
    echo "❌ API is not ready"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec api alembic upgrade head

# Create initial data
echo "📊 Creating initial cryptocurrency data..."
docker-compose exec api python -c "
import asyncio
from app.db.database import SessionLocal
from app.services.cryptocurrency_service import cryptocurrency_service
from app.models.cryptocurrency import Cryptocurrency

async def create_initial_data():
    db = SessionLocal()
    
    # Create some fake cryptocurrencies for demo
    cryptos = [
        {'symbol': 'BTC', 'name': 'Bitcoin', 'slug': 'bitcoin', 'current_price': 45000},
        {'symbol': 'ETH', 'name': 'Ethereum', 'slug': 'ethereum', 'current_price': 2800},
        {'symbol': 'BNB', 'name': 'Binance Coin', 'slug': 'binance-coin', 'current_price': 320},
        {'symbol': 'ADA', 'name': 'Cardano', 'slug': 'cardano', 'current_price': 0.45},
        {'symbol': 'SOL', 'name': 'Solana', 'slug': 'solana', 'current_price': 95},
        {'symbol': 'XRP', 'name': 'XRP', 'slug': 'xrp', 'current_price': 0.52},
        {'symbol': 'DOT', 'name': 'Polkadot', 'slug': 'polkadot', 'current_price': 6.8},
        {'symbol': 'DOGE', 'name': 'Dogecoin', 'slug': 'dogecoin', 'current_price': 0.08},
        {'symbol': 'AVAX', 'name': 'Avalanche', 'slug': 'avalanche', 'current_price': 18},
        {'symbol': 'MATIC', 'name': 'Polygon', 'slug': 'polygon', 'current_price': 0.85}
    ]
    
    for crypto_data in cryptos:
        existing = db.query(Cryptocurrency).filter(Cryptocurrency.symbol == crypto_data['symbol']).first()
        if not existing:
            crypto = Cryptocurrency(
                symbol=crypto_data['symbol'],
                name=crypto_data['name'],
                slug=crypto_data['slug'],
                current_price=crypto_data['current_price'],
                market_cap_rank=len(db.query(Cryptocurrency).all()) + 1
            )
            db.add(crypto)
    
    db.commit()
    db.close()
    print('✅ Initial cryptocurrency data created')

asyncio.run(create_initial_data())
"

# Create admin user
echo "👤 Creating admin user..."
docker-compose exec api python -c "
from app.db.database import SessionLocal
from app.services.user_service import UserService
from app.models.user import UserRole

db = SessionLocal()

try:
    admin_user = UserService.create_admin_user(
        db=db,
        username='admin',
        email='admin@trading.com',
        password='admin123',
        full_name='Trading Admin'
    )
    print(f'✅ Admin user created: {admin_user.username}')
except ValueError as e:
    print(f'ℹ️  Admin user already exists: {e}')

db.close()
"

echo ""
echo "🎉 Trading System is ready!"
echo ""
echo "📊 Access Points:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • API Base URL: http://localhost:8000/api/v1"
echo "   • Flower (Celery Monitor): http://localhost:5555"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "🔑 Default Admin Credentials:"
echo "   • Username: admin"
echo "   • Password: admin123"
echo ""
echo "🚀 Quick Start Trading:"
echo "   1. Login: POST /api/v1/auth/login"
echo "   2. Create Wallet: POST /api/v1/trading/wallet/create"
echo "   3. Buy Crypto: POST /api/v1/trading/buy"
echo "   4. Check Portfolio: GET /api/v1/trading/portfolio"
echo ""
echo "📈 To simulate market movements:"
echo "   POST /api/v1/trading/simulate-market (Admin only)"
echo ""
echo "🛑 To stop the system:"
echo "   docker-compose down"
echo ""