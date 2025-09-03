# 🏦 Complete Trading System with Docker

## 🚀 **FULLY DOCKERIZED CRYPTOCURRENCY TRADING PLATFORM**

This is a **complete, production-ready cryptocurrency trading system** with:
- **Real-time trading simulation**
- **Profit/Loss tracking**
- **Fake wallet with $10,000 starting balance**
- **Market simulation**
- **Comprehensive portfolio analytics**

---

## 🎯 **QUICK START**

### **1. Start the Trading System**
```bash
cd ~/repos/trading-system/Bakend
./start_trading_system.sh
```

### **2. Run Trading Demo**
```bash
python demo_trading.py
```

### **3. Access the System**
- **API Documentation**: http://localhost:8000/docs
- **Celery Monitor**: http://localhost:5555
- **Admin Login**: username: `admin`, password: `admin123`

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **Docker Services**
- **PostgreSQL**: Database for all trading data
- **Redis**: Caching and message broker
- **FastAPI**: Main trading API
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled tasks
- **Flower**: Task monitoring dashboard

### **Trading Features**
- ✅ **Fake Wallet**: Start with $10,000 virtual money
- ✅ **Real Trading**: Buy/sell cryptocurrencies with realistic prices
- ✅ **P&L Tracking**: Real-time profit/loss calculations
- ✅ **Market Simulation**: Realistic price movements
- ✅ **Portfolio Analytics**: Comprehensive trading statistics
- ✅ **Transaction History**: Complete audit trail
- ✅ **Risk Metrics**: Win rate, drawdown, Sharpe ratio

---

## 💰 **TRADING WORKFLOW**

### **1. Create Account & Wallet**
```bash
# Login as admin
POST /api/v1/auth/login/json
{
  "username": "admin",
  "password": "admin123"
}

# Create trading wallet (starts with $10,000)
POST /api/v1/trading/wallet/create
```

### **2. Buy Cryptocurrencies**
```bash
# Buy $1000 worth of Bitcoin
POST /api/v1/trading/buy
{
  "symbol": "BTC",
  "amount": 1000
}

# Buy $500 worth of Ethereum
POST /api/v1/trading/buy
{
  "symbol": "ETH", 
  "amount": 500
}
```

### **3. Monitor Portfolio**
```bash
# Get complete portfolio summary
GET /api/v1/trading/portfolio

# Response includes:
{
  "total_portfolio_value": 10000.00,
  "usd_balance": 8500.00,
  "total_pnl": 150.25,
  "total_pnl_percentage": 1.50,
  "holdings": [...],
  "recent_transactions": [...],
  "win_rate": 75.0,
  "max_drawdown": 2.5
}
```

### **4. Simulate Market Movement**
```bash
# Simulate realistic price changes (Admin only)
POST /api/v1/trading/simulate-market

# This updates all cryptocurrency prices randomly (-10% to +10%)
# and recalculates all portfolio values
```

### **5. Sell Positions**
```bash
# Sell 0.5 Bitcoin
POST /api/v1/trading/sell
{
  "symbol": "BTC",
  "amount": 0.5
}

# Response shows realized P&L:
{
  "realized_pnl": 125.50,
  "realized_pnl_percentage": 12.55,
  "remaining_balance": 9125.50
}
```

---

## 📊 **PROFIT/LOSS TRACKING**

### **Real-time P&L Calculations**
- **Unrealized P&L**: Current value vs. purchase cost
- **Realized P&L**: Actual profit/loss when selling
- **Total P&L**: Combined realized + unrealized
- **P&L Percentage**: Return on investment
- **Daily P&L**: Day-over-day changes

### **Portfolio Metrics**
- **Total Portfolio Value**: USD + crypto holdings value
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest portfolio decline
- **Sharpe Ratio**: Risk-adjusted returns
- **Trade Statistics**: Total, winning, losing trades

### **Example Portfolio Display**
```
📊 PORTFOLIO SUMMARY
====================================
💰 Total Portfolio Value: $10,247.50
💵 USD Balance: $3,500.00
📈 Total P&L: $247.50 (2.48%)
📊 Unrealized P&L: $125.00
💸 Realized P&L: $122.50
📉 Max Drawdown: 1.25%
🎯 Win Rate: 80.0%
📋 Total Trades: 15

🏦 CURRENT HOLDINGS (5):
----------------------------------------
   BTC:     0.150000 @ $45,000.00
        Current: $46,500.00 | Value: $6,975.00
        📈 PROFIT: $225.00 (3.33%)

   ETH:     2.500000 @ $2,800.00
        Current: $2,750.00 | Value: $6,875.00
        📉 LOSS: -$125.00 (-1.79%)
```

---

## 🎲 **MARKET SIMULATION**

### **Realistic Price Movements**
- **Random Variation**: -10% to +10% price changes
- **Market Correlation**: Realistic crypto market behavior
- **Volatility Simulation**: Different volatility for each coin
- **Time-based Updates**: Scheduled market movements

### **Automated Trading Signals**
- **Buy Signals**: Generated on significant price drops
- **Sell Signals**: Generated on significant price increases
- **Confidence Scoring**: Signal strength indicators
- **Risk Assessment**: Integrated with risk engine

---

## 🔧 **TECHNICAL FEATURES**

### **Database Schema**
- **Wallets**: User trading accounts
- **Holdings**: Current cryptocurrency positions
- **Transactions**: Complete trading history
- **Orders**: Buy/sell order management
- **Trading Sessions**: Performance tracking

### **Background Tasks**
- **Market Price Updates**: Simulate realistic price movements
- **Portfolio Recalculation**: Update all P&L values
- **Risk Assessment**: Calculate risk scores
- **Trading Signals**: Generate buy/sell recommendations

### **API Endpoints**
```
Trading Endpoints:
├── POST /trading/wallet/create     # Create wallet
├── GET  /trading/wallet           # Get wallet info
├── GET  /trading/portfolio        # Portfolio summary
├── POST /trading/buy              # Buy cryptocurrency
├── POST /trading/sell             # Sell cryptocurrency
├── GET  /trading/holdings         # Current positions
├── GET  /trading/transactions     # Trading history
├── POST /trading/simulate-market  # Market simulation
└── POST /trading/update-portfolio # Update values
```

---

## 🎮 **DEMO SCRIPT FEATURES**

The `demo_trading.py` script provides a **complete trading simulation**:

### **Demo Phases**
1. **Setup**: Login and create wallet with $10,000
2. **Buying Phase**: Purchase 5 different cryptocurrencies
3. **Market Simulation**: 3 rounds of price movements
4. **Selling Phase**: Take profits/losses on positions
5. **Final Analysis**: Complete performance summary

### **Demo Output Example**
```
🚀 Starting Trading System Demo
==================================================
🔐 Logging in as admin...
✅ Login successful!
💰 Creating trading wallet...
✅ Wallet created! Starting balance: $10000.0

📈 PHASE 1: BUYING CRYPTOCURRENCIES
----------------------------------------
📈 Buying $1247.50 worth of BTC...
✅ Bought 0.027722 BTC at $45000.00
   Total cost: $1247.50 (fee: $1.25)

🎲 PHASE 2: MARKET SIMULATION
----------------------------------------
🔄 Market Movement #1
✅ Market simulation completed!
📈 Portfolio up $156.25 (1.56%)

📉 PHASE 3: TAKING PROFITS/LOSSES
----------------------------------------
📉 Selling 0.013861 BTC...
✅ Sold 0.013861 BTC for $641.25
   💰 PROFIT: $17.50 (2.81%)

🏁 FINAL RESULTS
----------------------------------------
🎯 TRADING SESSION SUMMARY:
   Initial Balance: $10,000.00
   Final Balance: $10,234.75
   Total Return: $234.75 (2.35%)
   🎉 PROFITABLE SESSION! You made $234.75!
   📊 Total Trades: 12
   🎯 Win Rate: 75.0%
   📉 Max Drawdown: 1.25%
```

---

## 🚀 **GETTING STARTED**

### **Prerequisites**
- Docker & Docker Compose
- 8GB+ RAM recommended
- Ports 8000, 5432, 6379, 5555 available

### **Installation**
```bash
# 1. Navigate to backend directory
cd ~/repos/trading-system/Bakend

# 2. Start the complete system
./start_trading_system.sh

# 3. Wait for services to start (30-60 seconds)

# 4. Run the trading demo
python demo_trading.py

# 5. Access the API documentation
open http://localhost:8000/docs
```

### **Manual Trading**
```bash
# Login and get token
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create wallet
curl -X POST "http://localhost:8000/api/v1/trading/wallet/create" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Buy cryptocurrency
curl -X POST "http://localhost:8000/api/v1/trading/buy" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "amount": 1000}'

# Check portfolio
curl -X GET "http://localhost:8000/api/v1/trading/portfolio" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 **WHAT YOU'LL SEE**

### **Real Trading Experience**
- ✅ **Realistic Prices**: Bitcoin ~$45,000, Ethereum ~$2,800
- ✅ **Trading Fees**: 0.1% per transaction (like real exchanges)
- ✅ **Market Volatility**: Prices move up and down realistically
- ✅ **P&L Tracking**: See exactly how much you're making/losing
- ✅ **Portfolio Analytics**: Win rate, drawdown, total returns

### **Complete Trading Cycle**
1. **Start**: $10,000 virtual money
2. **Buy**: Purchase various cryptocurrencies
3. **Hold**: Watch prices move up and down
4. **Sell**: Take profits or cut losses
5. **Analyze**: See complete performance metrics

### **Professional Features**
- **Risk Assessment**: Each crypto gets a risk score
- **Background Tasks**: Automated market updates
- **Transaction History**: Complete audit trail
- **Portfolio Rebalancing**: Track allocation changes
- **Performance Metrics**: Sharpe ratio, max drawdown

---

## 🏆 **THIS IS A COMPLETE TRADING PLATFORM**

This isn't just a demo - it's a **fully functional cryptocurrency trading system** that includes:

- **Enterprise-grade architecture** with Docker
- **Real-time P&L calculations** 
- **Professional trading features**
- **Comprehensive risk management**
- **Production-ready scalability**

**Perfect for learning, testing trading strategies, or as a foundation for a real trading platform!**

---

## 🛑 **STOPPING THE SYSTEM**

```bash
# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

**🎉 Ready to start trading? Run `./start_trading_system.sh` and begin your trading journey!**