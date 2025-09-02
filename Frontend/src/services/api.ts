import axios from 'axios';
import type { Cryptocurrency, CryptocurrencyList, PriceHistoryList, DataUpdateResponse } from '../types/cryptocurrency';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const cryptocurrencyApi = {
  // Get list of cryptocurrencies with optional filters
  getCryptocurrencies: async (params?: {
    skip?: number;
    limit?: number;
    sort_by?: string;
    order?: 'asc' | 'desc';
    symbol_filter?: string;
    min_market_cap?: number;
    max_market_cap?: number;
    min_volume?: number;
  }): Promise<CryptocurrencyList> => {
    const response = await api.get('/cryptocurrencies/', { params });
    return response.data;
  },

  // Get specific cryptocurrency by symbol
  getCryptocurrency: async (symbol: string): Promise<Cryptocurrency> => {
    const response = await api.get(`/cryptocurrencies/${symbol}`);
    return response.data;
  },

  // Get price history for a cryptocurrency
  getPriceHistory: async (
    symbol: string,
    params?: {
      start_date?: string;
      end_date?: string;
      limit?: number;
    }
  ): Promise<PriceHistoryList> => {
    const response = await api.get(`/cryptocurrencies/${symbol}/history`, { params });
    return response.data;
  },

  // Get top cryptocurrencies by category
  getTopCryptocurrencies: async (
    category: 'market_cap' | 'volume' | 'gainers' | 'losers',
    limit: number = 10
  ): Promise<Cryptocurrency[]> => {
    const response = await api.get(`/cryptocurrencies/top/${category}`, {
      params: { limit }
    });
    return response.data;
  },

  // Sync cryptocurrency data
  syncCryptocurrencyData: async (params?: {
    limit?: number;
    provider?: 'coingecko' | 'coinmarketcap';
  }): Promise<DataUpdateResponse> => {
    const response = await api.post('/cryptocurrencies/sync', null, { params });
    return response.data;
  },
};

export default api;
