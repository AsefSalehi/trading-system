# 🚀 Trading System - Advanced Cryptocurrency Trading Platform

A full-stack cryptocurrency trading platform with real-time market data, portfolio management, and advanced trading features.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Production Deployment](#-production-deployment)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Features
- **Real-time Market Data**: Live cryptocurrency prices from multiple sources
- **Advanced Trading Interface**: Professional trading forms with order management
- **Portfolio Management**: Comprehensive portfolio tracking and analytics
- **Risk Assessment**: Advanced risk analysis and management tools
- **User Authentication**: Secure JWT-based authentication system
- **Responsive Design**: Mobile-first design with modern UI/UX

### 📊 Trading Features
- **Multi-Exchange Support**: Integration with major cryptocurrency exchanges
- **Order Management**: Market, limit, and stop orders
- **Portfolio Analytics**: Performance tracking and profit/loss analysis
- **Risk Management**: Position sizing and risk assessment
- **Transaction History**: Complete trading history and reporting

### 🎨 UI/UX Features
- **Modern Design**: Glass morphism and gradient designs
- **Smooth Animations**: Custom CSS animations and transitions
- **Dark/Light Theme**: Theme switching support
- **Mobile Responsive**: Optimized for all device sizes
- **Real-time Updates**: Live data updates with WebSocket support

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 4
- **State Management**: TanStack Query (React Query)
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT tokens
- **API Documentation**: OpenAPI/Swagger

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Process Management**: Supervisor
- **Environment**: Ubuntu 22.04

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd trading-system
```

### 2. Start the Backend
```bash
cd Bakend
./setup.sh
# Choose option 1 for Docker or option 2 for manual setup
```

### 3. Start the Frontend
```bash
cd Frontend
npm install
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
trading-system/
├── Frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── contexts/        # React contexts
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service layer
│   │   ├── types/           # TypeScript definitions
│   │   └── lib/             # Utility functions
│   ├── public/              # Static assets
│   └── dist/                # Production build
├── Bakend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── docker-compose.yml       # Docker services
└── README.md               # This file
```

## 🔧 Development

### Backend Development
```bash
cd Bakend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost/trading_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
COINMARKETCAP_API_KEY=your-api-key
COINGECKO_API_KEY=your-api-key
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Trading System
VITE_APP_VERSION=1.0.0
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

#### Backend
```bash
cd Bakend
pip install -r requirements.txt
alembic upgrade head
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Frontend
```bash
cd Frontend
npm run build:prod
# Serve dist/ folder with nginx or your preferred web server
```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/cryptocurrencies` - Get cryptocurrency data
- `POST /api/v1/trading/orders` - Place trading orders
- `GET /api/v1/portfolio/summary` - Get portfolio summary
- `GET /api/v1/risk/assessment` - Risk analysis

## 🧪 Testing

### Backend Tests
```bash
cd Bakend
pytest tests/ -v
```

### Frontend Tests
```bash
cd Frontend
npm run test
```

## 🔒 Security

- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control
- **Data Validation**: Pydantic models for API validation
- **SQL Injection**: SQLAlchemy ORM protection
- **XSS Protection**: Input sanitization
- **CORS**: Configured for production domains

## 📊 Performance

- **Frontend**: Lighthouse score 90+ on all metrics
- **Backend**: <100ms response time for most endpoints
- **Database**: Optimized queries with proper indexing
- **Caching**: Redis caching for frequently accessed data
- **CDN**: Static asset optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript/Python type hints
- Write comprehensive tests
- Update documentation
- Follow existing code style
- Use conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

## 🙏 Acknowledgments

- **CoinMarketCap API** for cryptocurrency data
- **CoinGecko API** for additional market data
- **React Community** for excellent libraries
- **FastAPI Community** for the amazing framework

---

**Built with ❤️ by the Trading System Team**

*Ready to revolutionize cryptocurrency trading!* 🚀