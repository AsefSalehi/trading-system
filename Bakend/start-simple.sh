#!/bin/bash

echo "🚀 Starting Docker services (simple approach)..."

# Stop any existing services
docker-compose down

# Use the simple docker-compose file without migration service
echo "🗄️ Starting database and Redis..."
docker-compose -f docker-compose-simple.yml up -d postgres redis

# Wait for database to be healthy
echo "⏳ Waiting for database to be ready..."
sleep 15

# Check database health
echo "🔍 Checking database health..."
docker-compose -f docker-compose-simple.yml exec postgres pg_isready -U user -d trading_db

# Start the API service
echo "🌐 Starting API service..."
docker-compose -f docker-compose-simple.yml up -d api

# Wait for API to start
echo "⏳ Waiting for API to start..."
sleep 10

# Check if API is running
if docker-compose -f docker-compose-simple.yml ps api | grep -q "Up"; then
    echo "✅ API service is running"

    # Run migration manually
    echo "🔄 Running database migration..."
    docker-compose -f docker-compose-simple.yml exec api alembic upgrade head

    if [ $? -eq 0 ]; then
        echo "✅ Database migration successful!"

        # Start remaining services
        echo "🔧 Starting worker services..."
        docker-compose -f docker-compose-simple.yml up -d worker beat flower

        # Wait for services to start
        sleep 5

        # Check status
        echo "🔍 Final status check..."
        docker-compose -f docker-compose-simple.yml ps

        # Test API
        echo "🧪 Testing API..."
        sleep 3
        curl -f http://localhost:8000/health && echo "✅ API is healthy!" || echo "❌ API health check failed"

        echo ""
        echo "🎉 Setup complete!"
        echo "🌐 Services available at:"
        echo "   API: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo "   Flower (Celery): http://localhost:5555"

    else
        echo "❌ Database migration failed"
        echo "📋 API logs:"
        docker-compose -f docker-compose-simple.yml logs api
    fi

else
    echo "❌ API service failed to start"
    echo "📋 API logs:"
    docker-compose -f docker-compose-simple.yml logs api
    echo ""
    echo "💡 Try manual setup instead: ./setup-manual.sh"
fi
