#!/bin/bash

# Trading System Health Check Script
# This script checks the health of both backend and frontend services

set -e

echo "🏥 Trading System Health Check"
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
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check if port is responding
check_port() {
    local port=$1
    local service=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" | grep -q "200\|404"; then
        print_success "$service is responding on port $port"
        return 0
    else
        print_error "$service is not responding on port $port"
        return 1
    fi
}

# Function to check backend health endpoint
check_backend_health() {
    local response=$(curl -s "http://localhost:8000/health" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q '"status":"healthy"'; then
        print_success "Backend health check passed"
        echo "   Status: $(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
        echo "   Version: $(echo "$response" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)"
        return 0
    else
        print_error "Backend health check failed"
        return 1
    fi
}

# Function to check process by PID
check_process() {
    local pid_file=$1
    local service=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_success "$service process is running (PID: $pid)"
            return 0
        else
            print_error "$service process is not running (stale PID file)"
            return 1
        fi
    else
        print_warning "$service PID file not found"
        return 1
    fi
}

# Check system resources
print_status "Checking system resources..."

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    print_success "Disk usage: ${DISK_USAGE}% (healthy)"
else
    print_warning "Disk usage: ${DISK_USAGE}% (high)"
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    print_success "Memory usage: ${MEMORY_USAGE}% (healthy)"
else
    print_warning "Memory usage: ${MEMORY_USAGE}% (high)"
fi

echo ""
print_status "Checking services..."

# Check backend
echo "Backend Service:"
BACKEND_HEALTHY=true

if ! check_process "backend.pid" "Backend"; then
    BACKEND_HEALTHY=false
fi

if ! check_port 8000 "Backend API"; then
    BACKEND_HEALTHY=false
fi

if ! check_backend_health; then
    BACKEND_HEALTHY=false
fi

echo ""

# Check frontend
echo "Frontend Service:"
FRONTEND_HEALTHY=true

if ! check_process "frontend.pid" "Frontend"; then
    FRONTEND_HEALTHY=false
fi

if ! check_port 5173 "Frontend"; then
    FRONTEND_HEALTHY=false
fi

echo ""

# Overall health summary
print_status "Health Summary:"
echo "================================"

if [ "$BACKEND_HEALTHY" = true ]; then
    print_success "Backend: Healthy"
else
    print_error "Backend: Unhealthy"
fi

if [ "$FRONTEND_HEALTHY" = true ]; then
    print_success "Frontend: Healthy"
else
    print_error "Frontend: Unhealthy"
fi

echo ""

if [ "$BACKEND_HEALTHY" = true ] && [ "$FRONTEND_HEALTHY" = true ]; then
    print_success "Overall System Status: HEALTHY 🟢"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    exit 0
else
    print_error "Overall System Status: UNHEALTHY 🔴"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Check logs: tail -f backend.log frontend.log"
    echo "   - Restart system: ./stop-system.sh && ./start-system.sh"
    echo "   - Check ports: netstat -tlnp | grep -E ':(8000|5173)'"
    exit 1
fi