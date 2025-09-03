#!/bin/bash

# Trading System Startup Script
# This script starts both the backend and frontend services

set -e

echo "🚀 Starting Trading System..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "start-system.sh" ]; then
    print_error "Please run this script from the trading-system root directory"
    exit 1
fi

# Check for required directories
if [ ! -d "Frontend" ] || [ ! -d "Bakend" ]; then
    print_error "Frontend or Bakend directory not found"
    exit 1
fi

print_status "Checking system requirements..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.12+ and try again."
    exit 1
fi

print_success "System requirements check passed"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
print_status "Checking port availability..."

if check_port 8000; then
    print_warning "Port 8000 is already in use. Backend might already be running."
else
    print_success "Port 8000 is available"
fi

if check_port 5173; then
    print_warning "Port 5173 is already in use. Frontend might already be running."
else
    print_success "Port 5173 is available"
fi

# Start Backend
print_status "Starting backend services..."
cd Bakend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
print_status "Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Start backend in background
print_status "Starting FastAPI backend on port 8000..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if check_port 8000; then
    print_success "Backend started successfully (PID: $BACKEND_PID)"
else
    print_error "Failed to start backend. Check backend.log for details."
    exit 1
fi

cd ..

# Start Frontend
print_status "Starting frontend services..."
cd Frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
print_status "Starting React frontend on port 5173..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if check_port 5173; then
    print_success "Frontend started successfully (PID: $FRONTEND_PID)"
else
    print_error "Failed to start frontend. Check frontend.log for details."
    exit 1
fi

cd ..

# Create PID file for easy management
echo "$BACKEND_PID" > backend.pid
echo "$FRONTEND_PID" > frontend.pid

print_success "Trading System started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Management:"
echo "   Stop system: ./stop-system.sh"
echo "   View logs: tail -f backend.log frontend.log"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
print_status "System is ready for trading! 🚀"