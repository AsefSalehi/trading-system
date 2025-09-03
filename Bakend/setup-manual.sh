#!/bin/bash

# Trading Backend API Manual Setup Script
# This script sets up the development environment without Docker

set -e  # Exit on any error

echo "🚀 Setting up Trading Backend API (Manual Setup)..."

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
    pip install --upgrade pip setuptools wheel
    
    # Install dependencies with timeout and retries
    echo "📥 Installing Python dependencies..."
    pip install --timeout=1000 --retries=5 -r requirements.txt
    
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

# Install and start PostgreSQL (macOS with Homebrew)
setup_postgresql_mac() {
    echo "🗄️ Setting up PostgreSQL..."
    
    if command -v brew &> /dev/null; then
        if ! brew list postgresql@15 &> /dev/null; then
            echo "Installing PostgreSQL..."
            brew install postgresql@15
        fi
        
        # Start PostgreSQL service
        brew services start postgresql@15
        
        # Create database
        createdb trading_db 2>/dev/null || echo "Database might already exist"
        
        echo "✅ PostgreSQL setup complete"
    else
        echo "⚠️ Homebrew not found. Please install PostgreSQL manually."
        echo "Visit: https://www.postgresql.org/download/"
    fi
}

# Install and start Redis (macOS with Homebrew)
setup_redis_mac() {
    echo "🔴 Setting up Redis..."
    
    if command -v brew &> /dev/null; then
        if ! brew list redis &> /dev/null; then
            echo "Installing Redis..."
            brew install redis
        fi
        
        # Start Redis service
        brew services start redis
        
        echo "✅ Redis setup complete"
    else
        echo "⚠️ Homebrew not found. Please install Redis manually."
        echo "Visit: https://redis.io/download"
    fi
}

# Run database migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run migrations
    alembic upgrade head
    
    echo "✅ Database migrations complete"
}

# Start services manually
start_services() {
    echo "🔧 Starting services..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    echo "Starting Celery worker (in background)..."
    celery -A app.core.celery_app worker --loglevel=info --detach
    
    echo "Starting Celery beat (in background)..."
    celery -A app.core.celery_app beat --loglevel=info --detach
    
    echo "Starting Flower (in background)..."
    celery -A app.core.celery_app flower --port=5555 --detach
    
    echo "🌐 Services started:"
    echo "   Flower (Celery): http://localhost:5555"
    echo ""
    echo "Starting FastAPI server..."
    echo "🌐 API will be available at: http://localhost:8000"
    echo "📚 API Documentation at: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Main setup function
main() {
    echo "🎯 Trading Backend API Manual Setup"
    echo "===================================="
    
    # Check prerequisites
    check_python
    
    # Setup environment
    setup_env
    setup_python_env
    
    # Detect OS and setup services
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 Detected macOS - setting up with Homebrew"
        setup_postgresql_mac
        setup_redis_mac
    else
        echo "🐧 Detected Linux/Other - please install PostgreSQL and Redis manually"
        echo "PostgreSQL: sudo apt-get install postgresql postgresql-contrib"
        echo "Redis: sudo apt-get install redis-server"
        read -p "Press Enter after installing PostgreSQL and Redis..."
    fi
    
    # Run migrations
    run_migrations
    
    # Start services
    start_services
}

# Run main function
main "$@"