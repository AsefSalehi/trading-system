# Trading System

A comprehensive cryptocurrency trading system with backend API and frontend dashboard.

## 📁 Project Structure

```
trading-backend/
├── Bakend/                    # Backend API Implementation
│   ├── Backend.md            # Backend requirements and tickets
│   ├── README.md             # Backend setup and documentation
│   ├── app/                  # FastAPI application
│   ├── alembic/              # Database migrations
│   ├── docker-compose.yml    # Backend services
│   └── ...                   # Backend implementation files
├── Frontend/                  # Frontend Implementation
│   └── Frontend.md           # Frontend requirements and tickets
└── Roles.md                  # System roles and permissions
```

## 🚀 Getting Started

### Backend API
The backend is a FastAPI-based cryptocurrency trading API with real-time data integration.

```bash
# Navigate to backend directory
cd Bakend/

# One command setup (recommended)
./final-setup.sh

# Or manual setup (alternative)
./setup-manual.sh
```

**Features:**
- RESTful API with cryptocurrency listings
- Real-time data from CoinGecko/CoinMarketCap
- PostgreSQL database with Redis caching
- Background tasks with Celery
- Comprehensive testing suite

**Access:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Monitoring: http://localhost:5555

### Frontend Dashboard
The frontend is a complete React-based dashboard for cryptocurrency analysis and trading.

```bash
cd Frontend/
npm install
npm run dev
```

**Features:**
- User authentication (login/register)
- Real-time cryptocurrency market data
- Trading interface (buy/sell orders)
- Portfolio management and tracking
- Risk analysis and alerts
- Responsive design for mobile/desktop

**Access:**
- Frontend: http://localhost:5173
- Connects to backend API automatically

## 📋 Implementation Status

### ✅ Completed
- **BACKEND-001**: API-Driven Cryptocurrency Listing Service
- **BACKEND-002**: Risk Assessment Engine
- **BACKEND-003**: Role-Based Authentication & Permissions
- **BACKEND-004**: Trading System with Wallet Management
- **BACKEND-005**: Portfolio Tracking and P&L Calculation
- **FRONTEND-001**: Complete React Application with TypeScript
- **FRONTEND-002**: Authentication Flow (Login/Register)
- **FRONTEND-003**: Market Analysis Dashboard
- **FRONTEND-004**: Trading Interface (Buy/Sell Orders)
- **FRONTEND-005**: Portfolio Management Dashboard
- **FRONTEND-006**: Risk Analysis and Reporting Dashboard

### 🔄 In Progress
- **BACKEND-006**: Advanced Risk Management Tools
- **BACKEND-007**: Enhanced Logging & Monitoring
- **BACKEND-008**: Reporting & Moderation Features

### 📅 Future Enhancements
- Real-time WebSocket connections
- Advanced charting and technical analysis
- Mobile application
- Social trading features
- Advanced order types (limit, stop-loss)

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **Redis** - Caching and session storage
- **Celery** - Background task processing
- **SQLAlchemy** - ORM for database operations

### Frontend
- **React 19** - Modern frontend framework with hooks
- **TypeScript** - Type-safe JavaScript development
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Query** - Server state management
- **Axios** - HTTP client for API integration
- **Lucide React** - Beautiful icon library

## 🤝 Contributing

1. Choose a component (Backend/Frontend)
2. Check the respective `.md` file for requirements
3. Follow the existing project structure
4. Add comprehensive tests
5. Update documentation

## 📖 Documentation

- [Backend Documentation](./Bakend/README.md)
- [Backend Requirements](./Bakend/Backend.md)
- [Frontend Requirements](./Frontend/Frontend.md)
- [System Roles](./Roles.md)

## 🔗 Quick Links

- [Backend API Docs](http://localhost:8000/docs) (when running)
- [Backend Setup Guide](./Bakend/README.md)
- [Implementation Summary](./Bakend/IMPLEMENTATION_SUMMARY.md)

---

**Note**: This is a practice trading system for educational purposes. Not intended for production financial trading.
