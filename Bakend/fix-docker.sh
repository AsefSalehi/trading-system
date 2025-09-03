#!/bin/bash

echo "🔧 Fixing Docker setup..."

# Stop all services and clean up
echo "🛑 Stopping all services and cleaning up..."
docker-compose down --volumes --remove-orphans

# Rebuild images to include the fix
echo "🔨 Rebuilding images with database connection fix..."
docker-compose build --no-cache

# Start only the database and redis first
echo "🗄️ Starting database and Redis..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 15

# Test database connection
echo "🔍 Testing database connection..."
docker-compose run --rm migrate python test-db-connection.py

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"

    # Now start all services
    echo "🚀 Starting all services..."
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
        echo "⚠️ Migration failed, trying manual approach..."
        docker-compose exec api alembic upgrade head
    fi

    # Test API
    echo "🧪 Testing API..."
    sleep 5
    curl -f http://localhost:8000/health && echo "✅ API is healthy!" || echo "❌ API health check failed"

    echo ""
    echo "🌐 Services available at:"
    echo "   API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Flower (Celery): http://localhost:5555"

else
    echo "❌ Database connection failed. Check PostgreSQL container:"
    docker-compose logs postgres
    echo ""
    echo "💡 Try manual setup instead: ./setup-manual.sh"
fi
