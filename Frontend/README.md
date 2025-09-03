# Trading System Frontend

A modern React-based frontend for the cryptocurrency trading system, built with TypeScript, Vite, and Tailwind CSS.

## Features

### 🔐 Authentication
- User registration and login
- JWT token-based authentication
- Secure session management
- Role-based access control

### 📊 Market Dashboard
- Real-time cryptocurrency listings
- Price charts and market data
- Top performers and market trends
- Advanced filtering and sorting

### 💰 Trading
- Buy/sell cryptocurrency orders
- Real-time portfolio tracking
- Transaction history
- Wallet management

### 📈 Portfolio Management
- Holdings overview with P&L
- Portfolio allocation charts
- Performance analytics
- Asset diversification tracking

### ⚠️ Risk Analysis
- Comprehensive risk assessment
- Risk metrics and scoring
- Real-time risk alerts
- Personalized recommendations

## Technology Stack

- **React 19** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Server state management
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend integrates with the FastAPI backend through:

- **Authentication API** - User login/register, token management
- **Cryptocurrency API** - Market data, price history, sync operations
- **Trading API** - Wallet operations, buy/sell orders, transactions
- **Risk API** - Risk assessment, metrics, alerts
- **Portfolio API** - Holdings, performance tracking

## Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_NODE_ENV=development
VITE_ENABLE_DEVTOOLS=true
```

## Project Structure

```
src/
├── components/          # React components
│   ├── Auth/           # Authentication components
│   ├── Layout/         # Layout and navigation
│   ├── Trading/        # Trading interface
│   ├── Portfolio/      # Portfolio management
│   └── Risk/           # Risk analysis
├── contexts/           # React contexts
├── services/           # API service layers
├── types/              # TypeScript type definitions
└── lib/                # Utility functions
```

## Key Components

### Authentication Flow
- `LoginForm` - User login interface
- `RegisterForm` - User registration
- `AuthContext` - Authentication state management

### Trading Interface
- `TradingDashboard` - Main trading interface
- `TradingForm` - Buy/sell order placement
- `WalletInfo` - Wallet balance and stats
- `TransactionHistory` - Trade history table

### Portfolio Management
- `PortfolioDashboard` - Portfolio overview
- `HoldingsTable` - Current positions
- `PortfolioChart` - Asset allocation visualization
- `PortfolioSummary` - Performance metrics

### Risk Analysis
- `RiskDashboard` - Risk overview
- `RiskMetricsCard` - Risk scoring and metrics
- `RiskAssessmentCard` - Detailed risk analysis
- `RiskAlertsTable` - Active risk alerts

## Development

### Code Style
- ESLint for code linting
- TypeScript for type safety
- Prettier for code formatting (recommended)

### State Management
- React Query for server state
- React Context for authentication
- Local state with useState/useReducer

### Styling
- Tailwind CSS for utility-first styling
- Responsive design for mobile/desktop
- Consistent color scheme and spacing

## Contributing

1. Follow the existing code structure
2. Use TypeScript for all new components
3. Add proper error handling
4. Include loading states for async operations
5. Ensure responsive design
6. Test with the backend API

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on port 8000
   - Check VITE_API_BASE_URL in .env file
   - Verify CORS settings in backend

2. **Authentication Issues**
   - Clear localStorage and try again
   - Check token expiration
   - Verify backend auth endpoints

3. **Build Errors**
   - Run `npm install` to update dependencies
   - Check TypeScript errors
   - Ensure all imports are correct

### Development Tips

- Use React DevTools for debugging
- Enable React Query DevTools in development
- Check browser console for errors
- Use network tab to debug API calls