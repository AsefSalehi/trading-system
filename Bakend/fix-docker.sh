#!/bin/bash

echo "🔧 Fixing Docker setup..."

# Stop all services
echo "🛑 Stopping all services..."
docker-compose down

# Start services with the new configuration
echo "🚀 Starting services with migration fix..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 20

# Check status
echo "🔍 Checking service status..."
docker-compose ps

# Check if migration completed
if docker-compose ps migrate | grep -q "Exit 0"; then
    echo "✅ Migration completed successfully"
else
    echo "⚠️ Migration status:"
    docker-compose ps migrate
    echo ""
    echo "📋 Migration logs:"
    docker-compose logs migrate
    echo ""
    echo "🔧 Trying manual migration..."
    docker-compose exec api alembic upgrade head
fi

# Test API
echo "🧪 Testing API..."
sleep 5
curl -f http://localhost:8000/health && echo "✅ API is healthy!" || echo "❌ API health check failed"

echo ""
echo "🌐 Services should be available at:"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Flower (Celery): http://localhost:5555"