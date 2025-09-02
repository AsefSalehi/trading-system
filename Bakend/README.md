# Trading Backend API

A comprehensive FastAPI-based cryptocurrency trading backend system that provides real-time cryptocurrency data, risk assessment, and portfolio management capabilities.

## 🚀 Features

### Core Features (BACKEND-001 ✅ COMPLETED)
- **RESTful API** with versioned endpoints (`/api/v1/`)
- **Real-time cryptocurrency data** from CoinGecko and CoinMarketCap
- **PostgreSQL database** with SQLAlchemy 2.x ORM
- **Redis caching** for performance optimization
- **Rate limiting** to prevent abuse
- **Background tasks** with Celery for data synchronization
- **Comprehensive OpenAPI documentation** at `/docs`

### API Endpoints

#### Cryptocurrency Listings
- `GET /api/v1/cryptocurrencies/` - List cryptocurrencies with filtering and sorting
- `GET /api/v1/cryptocurrencies/{symbol}` - Get specific cryptocurrency data
- `GET /api/v1/cryptocurrencies/{symbol}/history` - Get price history
- `GET /api/v1/cryptocurrencies/top/{category}` - Get top cryptocurrencies by category
- `POST /api/v1/cryptocurrencies/sync` - Manual data synchronization

#### System Endpoints
- `GET /health` - Health check
- `GET /` - API information

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Robust relational database
- **SQLAlchemy 2.x** - Modern Python SQL toolkit and ORM
- **Redis** - In-memory data structure store for caching
- **Celery** - Distributed task queue for background jobs
- **Pydantic** - Data validation using Python type annotations
- **Docker** - Containerization platform

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional but recommended)

## 🚀 Quick Start

**Important**: All commands should be run from the `Bakend/` directory.

```bash
cd Bakend/
```

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trading-backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Access the API**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Flower (Celery monitoring): http://localhost:5555

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb trading_db
   
   # Run migrations
   alembic upgrade head
   ```

3. **Start Redis**
   ```bash
   redis-server
   ```

4. **Start Celery worker** (in separate terminal)
   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   ```

5. **Start Celery beat** (in separate terminal)
   ```bash
   celery -A app.core.celery_app beat --loglevel=info
   ```

6. **Start the API server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | Secret key for security | Required |
| `COINMARKETCAP_API_KEY` | CoinMarketCap API key | Optional |
| `COINGECKO_API_KEY` | CoinGecko API key | Optional |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per minute | `60` |

### External API Keys

To get real cryptocurrency data, obtain API keys from:
- [CoinGecko](https://www.coingecko.com/en/api) (Free tier available)
- [CoinMarketCap](https://coinmarketcap.com/api/) (Free tier available)

## 📊 Data Sources

The system supports multiple cryptocurrency data providers:

- **CoinGecko** (Primary) - Comprehensive market data
- **CoinMarketCap** (Secondary) - Professional market data

Data is automatically synchronized every hour for top 200 cryptocurrencies and every 5 minutes for top 50.

## 🧪 Testing

### Run Unit Tests
```bash
pytest app/tests/unit/ -v
```

### Run Integration Tests
```bash
pytest app/tests/integration/ -v
```

### Run All Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f app/tests/load/test_load.py --host=http://localhost:8000
```

## 📖 API Usage Examples

### List Cryptocurrencies
```bash
# Get top 10 cryptocurrencies
curl "http://localhost:8000/api/v1/cryptocurrencies/?limit=10"

# Filter by symbol
curl "http://localhost:8000/api/v1/cryptocurrencies/?symbol_filter=BTC"

# Sort by market cap descending
curl "http://localhost:8000/api/v1/cryptocurrencies/?sort_by=market_cap&order=desc"
```

### Get Specific Cryptocurrency
```bash
curl "http://localhost:8000/api/v1/cryptocurrencies/BTC"
```

### Get Price History
```bash
curl "http://localhost:8000/api/v1/cryptocurrencies/BTC/history?limit=100"
```

### Manual Data Sync
```bash
curl -X POST "http://localhost:8000/api/v1/cryptocurrencies/sync?limit=50&provider=coingecko"
```

## 🏗️ Architecture

### Database Schema

#### Cryptocurrencies Table
- Basic information (symbol, name, slug)
- Market data (price, market cap, volume)
- Technical indicators (ATH, ATL, price changes)
- Metadata (description, website, images)

#### Price History Table
- Historical price data
- Market cap and volume snapshots
- Timestamp tracking

### Background Tasks

- **Hourly sync**: Updates top 200 cryptocurrencies
- **Frequent sync**: Updates top 50 cryptocurrencies every 5 minutes
- **Daily cleanup**: Removes old price history (1 year retention)

### Caching Strategy

- API responses cached for 5 minutes
- Automatic cache invalidation on data updates
- Redis-based distributed caching

## 🚦 API Rate Limiting

- **Default**: 60 requests per minute per IP
- **Sync endpoint**: 10 requests per minute per IP
- Rate limits are configurable via environment variables

## 📈 Monitoring

### Health Checks
- `GET /health` - Basic health status
- Database connectivity check
- Redis connectivity check

### Celery Monitoring
- Flower dashboard at http://localhost:5555
- Task status and history
- Worker monitoring

## 🔒 Security

- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Rate limiting to prevent abuse
- CORS configuration for web clients
- Environment-based configuration

## 🚀 Production Deployment

### Docker Production Setup
```bash
# Build production image
docker build -t trading-backend:latest .

# Run with production compose
docker-compose -f docker-compose.prod.yml up -d
```

### Performance Optimization
- Database connection pooling
- Redis caching
- Async request handling
- Background task processing
- Optimized database queries with indexes

## 🐛 Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check PostgreSQL is running
   - Verify connection string in `.env`

2. **Redis connection errors**
   - Ensure Redis is running
   - Check Redis URL configuration

3. **External API failures**
   - Verify API keys in environment
   - Check API rate limits
   - Monitor external service status

### Logs
```bash
# View API logs
docker-compose logs api

# View worker logs
docker-compose logs worker

# View all logs
docker-compose logs -f
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [CoinGecko](https://www.coingecko.com/) for cryptocurrency data
- [CoinMarketCap](https://coinmarketcap.com/) for market data

---

## Next Steps (Future Tickets)

This completes **BACKEND-001 - API-Driven Cryptocurrency Listing Service**. 

Upcoming tickets to implement:
- **BACKEND-002**: Risk Assessment Engine
- **BACKEND-003**: Role-Based Authentication & Permissions  
- **BACKEND-004**: Enhanced Task & Workflow Management
- **BACKEND-005**: Logging & Monitoring with Prometheus/Grafana
- **BACKEND-006**: Risk Management Tools
- **BACKEND-007**: Reporting & Moderation

For questions or support, please open an issue in the repository.