// Export all API services
export { authApi } from './authApi';
export { cryptocurrencyApi } from './api';
export { tradingApi } from './tradingApi';
export { riskApi } from './riskApi';
export { marketApi } from './marketApi';
export { advancedTradingApi } from './advancedTradingApi';
export { userApi } from './userApi';

// Export default api instance
export { default as api } from './api';

// Re-export types for convenience
export type { User, LoginRequest, RegisterRequest, TokenData } from '../types/auth';
export type { 
  Cryptocurrency, 
  CryptocurrencyList, 
  PriceHistory, 
  PriceHistoryList 
} from '../types/cryptocurrency';
export type { 
  Wallet, 
  TradeRequest, 
  TradeResponse, 
  Transaction, 
  Holding, 
  PortfolioSummary 
} from '../types/trading';