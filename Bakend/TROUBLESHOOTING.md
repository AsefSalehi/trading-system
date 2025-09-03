# Troubleshooting Guide

## Docker Build Timeout Issues

### Problem
Docker build fails with `ReadTimeoutError` when downloading Python packages, especially `psycopg2-binary`.

### Solutions

#### Option 1: Use Manual Setup (Recommended)
```bash
./setup-manual.sh
```
This bypasses Docker entirely and sets up the environment directly on your machine.

#### Option 2: Retry Docker Build
```bash
# Clean up and retry
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up -d
```

#### Option 3: Increase Docker Resources
1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase Memory to 4GB+ and CPU to 4+ cores
4. Apply & Restart Docker
5. Retry the build

#### Option 4: Use Different Base Image
Edit `Dockerfile` and change the first line to:
```dockerfile
FROM python:3.12-bullseye
```

### Manual Setup Requirements

#### macOS (with Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Create database
createdb trading_db
```

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Install Redis
sudo apt-get install redis-server

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server

# Create database
sudo -u postgres createdb trading_db
```

## Common Issues

### 1. Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### 2. Database Connection Issues
```bash
# Check PostgreSQL status
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Test connection
psql -h localhost -U user -d trading_db
```

### 3. Redis Connection Issues
```bash
# Check Redis status
brew services list | grep redis  # macOS
sudo systemctl status redis      # Linux

# Test connection
redis-cli ping
```

### 4. Python Virtual Environment Issues
```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 5. Alembic Migration Issues
```bash
# Reset migrations (CAUTION: This will drop all data)
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Environment Variables

Make sure your `.env` file has the correct values:

```env
# For manual setup
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/trading_db
REDIS_URL=redis://localhost:6379/0

# For Docker setup
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/trading_db
REDIS_URL=redis://redis:6379/0

# Required for all setups
SECRET_KEY=your-secret-key-here-please-change-in-production
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here
```

## Testing the Setup

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. API Documentation
Open: http://localhost:8000/docs

### 3. Database Connection
```bash
# From within the project directory
source venv/bin/activate
python -c "from app.db.database import engine; print('Database connected!')"
```

### 4. Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

## Getting Help

If you're still having issues:

1. Check the logs:
   ```bash
   # Docker logs
   docker-compose logs api
   
   # Manual setup logs
   tail -f app.log
   ```

2. Verify all services are running:
   ```bash
   # Check ports
   netstat -tulpn | grep -E ':(8000|5432|6379|5555)'
   ```

3. Test individual components:
   ```bash
   # Test FastAPI
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # Test Celery
   celery -A app.core.celery_app worker --loglevel=info
   ```

## Performance Tips

1. **Use SSD storage** for better Docker build performance
2. **Increase Docker memory** to 4GB+ for large builds
3. **Use manual setup** for development (faster iteration)
4. **Use Docker** for production deployment
5. **Cache pip packages** by mounting a volume:
   ```yaml
   volumes:
     - pip-cache:/root/.cache/pip
   ```