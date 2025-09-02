#!/bin/bash

# Trading Backend API Setup Script
# This script sets up the development environment for the Trading Backend API

set -e  # Exit on any error

echo "🚀 Setting up Trading Backend API (from Bakend directory)..."

# Check if Python 3.11+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo "✅ Python $PYTHON_VERSION found"
    else
        echo "❌ Python 3.11+ is required. Please install Python first."
        exit 1
    fi
}

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        echo "✅ Docker found"
        if command -v docker-compose &> /dev/null; then
            echo "✅ Docker Compose found"
        else
            echo "❌ Docker Compose is required. Please install Docker Compose."
            exit 1
        fi
    else
        echo "⚠️ Docker not found. You can still run manually, but Docker is recommended."
    fi
}

# Create virtual environment
setup_python_env() {
    echo "📦 Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    
    echo "✅ Python dependencies installed"
}

# Set up environment variables
setup_env() {
    echo "⚙️ Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "✅ Environment file created from template"
        echo "⚠️ Please edit .env file with your configuration before proceeding"
    else
        echo "✅ Environment file already exists"
    fi
}

# Set up database (if running manually)
setup_database() {
    echo "🗄️ Setting up database..."
    
    # Check if PostgreSQL is running
    if command -v psql &> /dev/null; then
        echo "✅ PostgreSQL client found"
        
        # Try to create database
        createdb trading_db 2>/dev/null || echo "Database might already exist"
        
        # Run migrations
        echo "🔄 Running database migrations..."
        alembic upgrade head
        
        echo "✅ Database setup complete"
    else
        echo "⚠️ PostgreSQL not found. Using Docker setup or install PostgreSQL manually."
    fi
}

# Start services with Docker
start_docker_services() {
    echo "🐳 Starting services with Docker..."
    
    if command -v docker-compose &> /dev/null; then
        # Build and start services
        docker-compose up -d
        
        # Wait for services to be ready
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        # Run database migrations
        echo "🔄 Running database migrations..."
        docker-compose exec api alembic upgrade head
        
        echo "✅ Docker services started successfully!"
        echo ""
        echo "🌐 Services available at:"
        echo "   API: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo "   Flower (Celery): http://localhost:5555"
        
    else
        echo "❌ Docker Compose not available"
        return 1
    fi
}

# Start services manually
start_manual_services() {
    echo "🔧 Starting services manually..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    echo "Starting Redis (in background)..."
    redis-server --daemonize yes 2>/dev/null || echo "⚠️ Redis might already be running or not installed"
    
    echo "Starting Celery worker (in background)..."
    celery -A app.core.celery_app worker --loglevel=info --detach
    
    echo "Starting Celery beat (in background)..."
    celery -A app.core.celery_app beat --loglevel=info --detach
    
    echo "Starting FastAPI server..."
    echo "🌐 API will be available at: http://localhost:8000"
    echo "📚 API Documentation at: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Main setup function
main() {
    echo "🎯 Trading Backend API Setup"
    echo "=============================="
    
    # Check prerequisites
    check_python
    check_docker
    
    # Setup environment
    setup_env
    
    # Ask user for setup preference
    echo ""
    echo "Choose setup method:"
    echo "1) Docker (Recommended - includes all services)"
    echo "2) Manual (Requires PostgreSQL and Redis installed)"
    echo "3) Exit"
    echo ""
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            echo "🐳 Using Docker setup..."
            if start_docker_services; then
                echo ""
                echo "🎉 Setup complete! Your Trading Backend API is ready."
                echo ""
                echo "Next steps:"
                echo "1. Check the API: curl http://localhost:8000/health"
                echo "2. View documentation: http://localhost:8000/docs"
                echo "3. Add your API keys to .env file for external data"
                echo ""
                echo "To stop services: docker-compose down"
            else
                echo "❌ Docker setup failed. Try manual setup."
                exit 1
            fi
            ;;
        2)
            echo "🔧 Using manual setup..."
            setup_python_env
            setup_database
            start_manual_services
            ;;
        3)
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