import api from './api';

export interface MarketOverview {
  total_market_cap: number;
  total_volume: number;
  market_cap_change_24h: number;
  volume_change_24h: number;
  active_cryptocurrencies: number;
  market_cap_percentage: Record<string, number>;
}

export interface RealTimePrice {
  symbol: string;
  price: number;
  source: string;
  timestamp?: string;
}

export interface Ticker24h {
  symbol: string;
  price: number;
  price_change: number;
  price_change_percent: number;
  high_price: number;
  low_price: number;
  volume: number;
  quote_volume: number;
  open_price: number;
  prev_close_price: number;
  count: number;
  last_update: string;
  source: string;
}

export interface HistoricalDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  quote_volume: number;
}

export interface HistoricalData {
  symbol: string;
  interval: string;
  data: HistoricalDataPoint[];
  count: number;
  source: string;
}

export interface TopCryptocurrency {
  symbol: string;
  name: string;
  price: number;
  price_change_24h: number;
  price_change_percentage_24h: number;
  volume_24h: number;
  quote_volume_24h: number;
  high_24h: number;
  low_24h: number;
  market_cap_rank: number;
  last_updated: string;
}

export const marketApi = {
  // Market overview
  getMarketOverview: async (): Promise<MarketOverview> => {
    const response = await api.get('/market/overview');
    return response.data;
  },

  // Real-time prices
  getRealTimePrice: async (symbol: string): Promise<RealTimePrice> => {
    const response = await api.get(`/market/price/${symbol}`);
    return response.data;
  },

  getMultiplePrices: async (symbols: string[]): Promise<{
    prices: RealTimePrice[];
    total_symbols: number;
    requested_symbols: number;
    timestamp: Record<string, string>;
  }> => {
    const symbolsParam = symbols.join(',');
    const response = await api.get('/market/prices', {
      params: { symbols: symbolsParam }
    });
    return response.data;
  },

  // 24h ticker
  get24hTicker: async (symbol: string): Promise<Ticker24h> => {
    const response = await api.get(`/market/ticker/${symbol}`);
    return response.data;
  },

  // Historical data
  getHistoricalData: async (
    symbol: string,
    interval: string = '1h',
    limit: number = 100
  ): Promise<HistoricalData> => {
    const response = await api.get(`/market/historical/${symbol}`, {
      params: { interval, limit }
    });
    return response.data;
  },

  // Top cryptocurrencies
  getTopCryptocurrencies: async (limit: number = 20): Promise<{
    cryptocurrencies: TopCryptocurrency[];
    count: number;
    source: string;
    last_updated: string | null;
  }> => {
    const response = await api.get('/market/top', {
      params: { limit }
    });
    return response.data;
  },

  // Market status
  getMarketStatus: async (): Promise<{
    status: string;
    message: string;
    binance_connected: boolean;
    last_update: string;
  }> => {
    const response = await api.get('/market/status');
    return response.data;
  },

  // Admin functions
  syncMarketData: async (symbols?: string[]): Promise<{
    message: string;
    updated_count: number;
    timestamp: string;
  }> => {
    const params = symbols ? { symbols: symbols.join(',') } : undefined;
    const response = await api.post('/market/sync', null, { params });
    return response.data;
  },

  startRealTimeUpdates: async (symbols?: string[]): Promise<{
    status: string;
    message: string;
    symbols: string[];
  }> => {
    const params = symbols ? { symbols: symbols.join(',') } : undefined;
    const response = await api.post('/market/start-realtime', null, { params });
    return response.data;
  },

  stopRealTimeUpdates: async (): Promise<{
    status: string;
    message: string;
  }> => {
    const response = await api.post('/market/stop-realtime');
    return response.data;
  },
};