import api from './api';
import type { 
  Wallet, 
  TradeRequest, 
  TradeResponse, 
  Transaction, 
  Holding, 
  PortfolioSummary 
} from '../types/trading';

export const tradingApi = {
  // Wallet operations
  createWallet: async (): Promise<Wallet> => {
    const response = await api.post('/trading/wallet/create');
    return response.data;
  },

  getWallet: async (): Promise<Wallet> => {
    const response = await api.get('/trading/wallet');
    return response.data;
  },

  // Portfolio operations
  getPortfolioSummary: async (): Promise<PortfolioSummary> => {
    const response = await api.get('/trading/portfolio');
    return response.data;
  },

  updatePortfolioValues: async (): Promise<{ message: string }> => {
    const response = await api.post('/trading/update-portfolio');
    return response.data;
  },

  // Trading operations
  buyCryptocurrency: async (tradeRequest: TradeRequest): Promise<TradeResponse> => {
    const response = await api.post('/trading/buy', tradeRequest);
    return response.data;
  },

  sellCryptocurrency: async (tradeRequest: TradeRequest): Promise<TradeResponse> => {
    const response = await api.post('/trading/sell', tradeRequest);
    return response.data;
  },

  // Transaction history
  getTransactions: async (params?: {
    limit?: number;
    transaction_type?: string;
  }): Promise<Transaction[]> => {
    const response = await api.get('/trading/transactions', { params });
    return response.data;
  },

  // Holdings
  getHoldings: async (): Promise<Holding[]> => {
    const response = await api.get('/trading/holdings');
    return response.data;
  },

  // Admin operations
  simulateMarketMovement: async (): Promise<{ message: string }> => {
    const response = await api.post('/trading/simulate-market');
    return response.data;
  },
};