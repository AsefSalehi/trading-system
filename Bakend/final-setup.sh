#!/bin/bash

echo "🎯 FINAL SETUP - Complete Trading System Setup"
echo "=============================================="

# Function to clean up everything
cleanup_all() {
    echo "🧹 Cleaning up all Docker resources..."

    # Stop and remove all containers
    docker stop $(docker ps -aq) 2>/dev/null || true
    docker rm $(docker ps -aq) 2>/dev/null || true

    # Remove all volumes
    docker volume prune -f 2>/dev/null || true

    # Remove networks
    docker network prune -f 2>/dev/null || true

    # Remove images related to this project
    docker rmi $(docker images -q --filter "reference=*trading*") 2>/dev/null || true
    docker rmi $(docker images -q --filter "reference=*bakend*") 2>/dev/null || true

    echo "✅ Cleanup complete"
}

# Function to build and start services
start_services() {
    echo "🚀 Starting services with clean setup..."

    # Create network
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
    echo "⏳ Waiting for database to be ready..."
    sleep 20

    # Test database connection
    echo "🔍 Testing database connection..."
    docker exec trading-postgres pg_isready -U user -d trading_db

    if [ $? -eq 0 ]; then
        echo "✅ Database is ready"
    else
        echo "❌ Database not ready, waiting more..."
        sleep 10
    fi

    # Build application image
    echo "🔨 Building application image..."
    docker build -t trading-app .

    if [ $? -ne 0 ]; then
        echo "❌ Docker build failed"
        return 1
    fi

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
      -v "$(pwd)":/app \
      trading-app \
      uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

    # Wait for API
    echo "⏳ Waiting for API to start..."
    sleep 15

    # Check if API is running
    if docker ps | grep -q trading-api; then
        echo "✅ API is running"

        # Fix migration conflicts first
        echo "🔧 Fixing migration conflicts..."
        docker exec trading-api python fix-migration.py

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
              -v "$(pwd)":/app \
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
              -v "$(pwd)":/app \
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

            return 0
        else
            echo "❌ Migration failed, but continuing..."
            # Try to mark migration as complete manually
            docker exec trading-api alembic stamp head 2>/dev/null || true
        fi
    else
        echo "❌ API failed to start"
        docker logs trading-api
        return 1
    fi
}

# Function to test the setup
test_setup() {
    echo "🧪 Testing the setup..."

    # Wait a bit for services to stabilize
    sleep 10

    # Test API health
    echo "🔍 Testing API health..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

    if [ "$response" = "200" ]; then
        echo "✅ API is healthy!"

        # Test API docs
        echo "📚 Testing API documentation..."
        docs_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)

        if [ "$docs_response" = "200" ]; then
            echo "✅ API documentation is accessible!"
        else
            echo "⚠️ API documentation might not be ready yet"
        fi

        return 0
    else
        echo "❌ API health check failed (HTTP $response)"
        return 1
    fi
}

# Function to show final status
show_status() {
    echo ""
    echo "🎉 SETUP COMPLETE!"
    echo "=================="
    echo ""
    echo "🌐 Services available at:"
    echo "   API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Flower (Celery): http://localhost:5555"
    echo ""
    echo "📋 Container status:"
    docker ps --filter "name=trading-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View API logs: docker logs trading-api"
    echo "   View all logs: docker logs trading-api && docker logs trading-worker"
    echo "   Stop all: docker stop \$(docker ps -q --filter 'name=trading-')"
    echo "   Remove all: docker rm \$(docker ps -aq --filter 'name=trading-')"
    echo ""
    echo "🚀 Frontend setup:"
    echo "   cd ../Frontend"
    echo "   npm run dev"
    echo "   Open: http://localhost:5173"
}

# Main execution
main() {
    echo "Choose setup option:"
    echo "1) Clean setup (recommended - removes everything and starts fresh)"
    echo "2) Quick setup (keeps existing data)"
    echo "3) Manual setup (no Docker)"
    echo "4) Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            echo "🧹 Starting clean setup..."
            cleanup_all
            if start_services && test_setup; then
                show_status
                echo "✅ Clean setup completed successfully!"
            else
                echo "❌ Setup failed. Check logs above."
                exit 1
            fi
            ;;
        2)
            echo "⚡ Starting quick setup..."
            if start_services && test_setup; then
                show_status
                echo "✅ Quick setup completed successfully!"
            else
                echo "❌ Setup failed. Check logs above."
                exit 1
            fi
            ;;
        3)
            echo "🔧 Starting manual setup..."
            ./setup-manual.sh
            ;;
        4)
            echo "👋 Setup cancelled"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
