#!/bin/bash

echo "🗄️ Resetting database for clean migration..."

# Stop services
echo "🛑 Stopping services..."
docker-compose -f docker-compose-simple.yml down

# Remove database volume to start fresh
echo "🧹 Removing database volume..."
docker volume rm bakend_postgres_data 2>/dev/null || true

# Start database and Redis
echo "🚀 Starting fresh database..."
docker-compose -f docker-compose-simple.yml up -d postgres redis

# Wait for database
echo "⏳ Waiting for database to initialize..."
sleep 20

# Check database health
echo "🔍 Checking database health..."
docker-compose -f docker-compose-simple.yml exec postgres pg_isready -U user -d trading_db

# Start API
echo "🌐 Starting API..."
docker-compose -f docker-compose-simple.yml up -d api

# Wait for API
echo "⏳ Waiting for API to start..."
sleep 10

# Run migration on fresh database
echo "🔄 Running migration on fresh database..."
docker-compose -f docker-compose-simple.yml exec api alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migration successful!"
    
    # Start remaining services
    echo "🔧 Starting remaining services..."
    docker-compose -f docker-compose-simple.yml up -d worker beat flower
    
    # Test API
    echo "🧪 Testing API..."
    sleep 5
    curl -f http://localhost:8000/health && echo "✅ API is healthy!" || echo "❌ API health check failed"
    
    echo ""
    echo "🎉 Database reset and setup complete!"
    echo "🌐 Services available at:"
    echo "   API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Flower (Celery): http://localhost:5555"
    
else
    echo "❌ Migration failed even on fresh database"
    echo "📋 API logs:"
    docker-compose -f docker-compose-simple.yml logs api
fi