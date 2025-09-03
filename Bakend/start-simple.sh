#!/bin/bash

echo "🚀 Starting Docker services (simple approach)..."

# Stop any existing services
docker-compose down

# Start only the core services (skip migration service)
echo "🗄️ Starting database and Redis..."
docker-compose up -d postgres redis

# Wait for database
echo "⏳ Waiting for database..."
sleep 15

# Start the API service
echo "🌐 Starting API service..."
docker-compose up -d api

# Wait for API to start
sleep 10

# Run migration manually
echo "🔄 Running database migration..."
docker-compose exec api alembic upgrade head

# Start remaining services
echo "🔧 Starting worker services..."
docker-compose up -d worker beat flower

# Check status
echo "🔍 Final status check..."
docker-compose ps

# Test API
echo "🧪 Testing API..."
curl -f http://localhost:8000/health && echo "✅ API is healthy!" || echo "❌ API health check failed"

echo ""
echo "🎉 Setup complete!"
echo "🌐 Services available at:"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Flower (Celery): http://localhost:5555"