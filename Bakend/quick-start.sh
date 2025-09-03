#!/bin/bash

echo "⚡ Quick Docker Start (bypassing docker-compose issues)..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker stop $(docker ps -q --filter "name=trading-") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=trading-") 2>/dev/null || true

# Create network
echo "🌐 Creating Docker network..."
docker network create trading-network 2>/dev/null || true

# Start PostgreSQL
echo "🗄️ Starting PostgreSQL..."
docker run -d \
  --name trading-postgres \
  --network trading-network \
  -e POSTGRES_DB=trading_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# Start Redis
echo "🔴 Starting Redis..."
docker run -d \
  --name trading-redis \
  --network trading-network \
  -p 6379:6379 \
  redis:7-alpine

# Wait for database
echo "⏳ Waiting for database..."
sleep 15

# Build our app image
echo "🔨 Building application image..."
docker build -t trading-app .

# Start API
echo "🌐 Starting API..."
docker run -d \
  --name trading-api \
  --network trading-network \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:password@trading-postgres:5432/trading_db \
  -e REDIS_URL=redis://trading-redis:6379/0 \
  -e CELERY_BROKER_URL=redis://trading-redis:6379/0 \
  -e CELERY_RESULT_BACKEND=redis://trading-redis:6379/0 \
  -e SECRET_KEY=your-secret-key-here \
  -v $(pwd):/app \
  trading-app \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Wait for API
echo "⏳ Waiting for API..."
sleep 10

# Run migration
echo "🔄 Running database migration..."
docker exec trading-api alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migration successful!"
    
    # Start Celery worker
    echo "👷 Starting Celery worker..."
    docker run -d \
      --name trading-worker \
      --network trading-network \
      -e DATABASE_URL=postgresql+asyncpg://user:password@trading-postgres:5432/trading_db \
      -e REDIS_URL=redis://trading-redis:6379/0 \
      -e CELERY_BROKER_URL=redis://trading-redis:6379/0 \
      -e CELERY_RESULT_BACKEND=redis://trading-redis:6379/0 \
      -v $(pwd):/app \
      trading-app \
      celery -A app.core.celery_app worker --loglevel=info
    
    # Start Celery beat
    echo "⏰ Starting Celery beat..."
    docker run -d \
      --name trading-beat \
      --network trading-network \
      -e DATABASE_URL=postgresql+asyncpg://user:password@trading-postgres:5432/trading_db \
      -e REDIS_URL=redis://trading-redis:6379/0 \
      -e CELERY_BROKER_URL=redis://trading-redis:6379/0 \
      -e CELERY_RESULT_BACKEND=redis://trading-redis:6379/0 \
      -v $(pwd):/app \
      trading-app \
      celery -A app.core.celery_app beat --loglevel=info
    
    # Start Flower
    echo "🌸 Starting Flower..."
    docker run -d \
      --name trading-flower \
      --network trading-network \
      -p 5555:5555 \
      -e CELERY_BROKER_URL=redis://trading-redis:6379/0 \
      -e CELERY_RESULT_BACKEND=redis://trading-redis:6379/0 \
      trading-app \
      celery -A app.core.celery_app flower --port=5555
    
    # Test API
    echo "🧪 Testing API..."
    sleep 5
    curl -f http://localhost:8000/health && echo "✅ API is healthy!" || echo "❌ API health check failed"
    
    echo ""
    echo "🎉 Setup complete!"
    echo "🌐 Services available at:"
    echo "   API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Flower (Celery): http://localhost:5555"
    echo ""
    echo "📋 Container status:"
    docker ps --filter "name=trading-"
    echo ""
    echo "🛑 To stop all services: docker stop \$(docker ps -q --filter 'name=trading-')"
    
else
    echo "❌ Migration failed"
    echo "📋 API logs:"
    docker logs trading-api
fi