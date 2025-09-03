#!/bin/bash

# Trading System Stop Script
# This script stops both the backend and frontend services

set -e

echo "🛑 Stopping Trading System..."
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
if [ ! -f "stop-system.sh" ]; then
    print_error "Please run this script from the trading-system root directory"
    exit 1
fi

# Function to stop process by PID
stop_process() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        print_status "Stopping $name (PID: $pid)..."
        kill "$pid"
        
        # Wait for process to stop
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "Force killing $name..."
            kill -9 "$pid"
        fi
        
        print_success "$name stopped successfully"
    else
        print_warning "$name is not running or PID not found"
    fi
}

# Stop backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    stop_process "$BACKEND_PID" "Backend"
    rm -f backend.pid
else
    print_warning "Backend PID file not found"
    # Try to find and kill uvicorn processes
    UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" || true)
    if [ -n "$UVICORN_PIDS" ]; then
        print_status "Found running uvicorn processes, stopping them..."
        echo "$UVICORN_PIDS" | xargs kill
        print_success "Uvicorn processes stopped"
    fi
fi

# Stop frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    stop_process "$FRONTEND_PID" "Frontend"
    rm -f frontend.pid
else
    print_warning "Frontend PID file not found"
    # Try to find and kill npm/vite processes
    NPM_PIDS=$(pgrep -f "npm run dev" || true)
    VITE_PIDS=$(pgrep -f "vite" || true)
    
    if [ -n "$NPM_PIDS" ]; then
        print_status "Found running npm processes, stopping them..."
        echo "$NPM_PIDS" | xargs kill
        print_success "NPM processes stopped"
    fi
    
    if [ -n "$VITE_PIDS" ]; then
        print_status "Found running vite processes, stopping them..."
        echo "$VITE_PIDS" | xargs kill
        print_success "Vite processes stopped"
    fi
fi

# Clean up log files (optional)
read -p "Do you want to clear log files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f backend.log frontend.log
    print_success "Log files cleared"
fi

print_success "Trading System stopped successfully!"
echo ""
print_status "To start the system again, run: ./start-system.sh"