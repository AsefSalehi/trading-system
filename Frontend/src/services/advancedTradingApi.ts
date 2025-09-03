import api from './api';

export interface OrderRequest {
  symbol: string;
  side: 'buy' | 'sell';
  amount: number;
  quantity: number;
  price: number;
}

export interface OrderResponse {
  order_id: number;
  status: string;
  order_type: string;
  symbol: string;
  side: string;
  quantity: number;
  price?: number;
  stop_price?: number;
  target_price?: number;
  executed_price?: number;
  created_at: string;
  executed_at?: string;
}

export interface RiskMetricsResponse {
  total_portfolio_value: number;
  cash_percentage: number;
  largest_position_percentage: number;
  daily_pnl_percentage: number;
  total_pnl_percentage: number;
  concentration_risk_score: number;
  overall_risk_score: number;
  recommendations: string[];
}

export interface ArbitrageOpportunity {
  symbol: string;
  buy_exchange: string;
  sell_exchange: string;
  buy_price: number;
  sell_price: number;
  profit_percentage: number;
  profit_amount: number;
  max_volume: number;
  timestamp: string;
}

export interface ExchangePrice {
  exchange: string;
  price: number;
  volume: number;
  timestamp: string;
}

export interface OrderBook {
  symbol: string;
  bids: Array<[number, number]>; // [price, quantity]
  asks: Array<[number, number]>; // [price, quantity]
  timestamp: string;
}

export const advancedTradingApi = {
  // Advanced Order Types
  placeLimitOrder: async (orderRequest: OrderRequest): Promise<OrderResponse> => {
    const response = await api.post('/advanced/orders/limit', orderRequest);
    return response.data;
  },

  placeStopLossOrder: async (
    symbol: string,
    quantity: number,
    stopPrice: number
  ): Promise<OrderResponse> => {
    const response = await api.post('/advanced/orders/stop-loss', {
      symbol,
      quantity,
      stop_price: stopPrice
    });
    return response.data;
  },

  placeTakeProfitOrder: async (
    symbol: string,
    quantity: number,
    targetPrice: number
  ): Promise<OrderResponse> => {
    const response = await api.post('/advanced/orders/take-profit', {
      symbol,
      quantity,
      target_price: targetPrice
    });
    return response.data;
  },

  // Order Management
  getOrders: async (statusFilter?: string): Promise<OrderResponse[]> => {
    const params = statusFilter ? { status_filter: statusFilter } : undefined;
    const response = await api.get('/advanced/orders', { params });
    return response.data;
  },

  cancelOrder: async (orderId: number): Promise<{ message: string }> => {
    const response = await api.delete(`/advanced/orders/${orderId}`);
    return response.data;
  },

  // Risk Management
  getRiskMetrics: async (): Promise<RiskMetricsResponse> => {
    const response = await api.get('/advanced/risk/metrics');
    return response.data;
  },

  performEmergencyRiskCheck: async (): Promise<{
    status: string;
    risk_level: string;
    actions_taken: string[];
    recommendations: string[];
  }> => {
    const response = await api.get('/advanced/risk/emergency-check');
    return response.data;
  },

  // Multi-Exchange & Arbitrage
  getExchangePrices: async (symbol: string): Promise<{
    symbol: string;
    prices: Record<string, ExchangePrice>;
    count: number;
  }> => {
    const response = await api.get(`/advanced/exchanges/prices/${symbol}`);
    return response.data;
  },

  getBestPrice: async (symbol: string, side: 'buy' | 'sell'): Promise<{
    symbol: string;
    side: string;
    best_exchange: string;
    best_price: number;
  }> => {
    const response = await api.get(`/advanced/exchanges/best-price/${symbol}`, {
      params: { side }
    });
    return response.data;
  },

  getArbitrageOpportunities: async (minProfit?: number): Promise<ArbitrageOpportunity[]> => {
    const params = minProfit ? { min_profit: minProfit } : undefined;
    const response = await api.get('/advanced/arbitrage/opportunities', { params });
    return response.data;
  },

  getOrderBooks: async (symbol: string): Promise<{
    symbol: string;
    order_books: Record<string, OrderBook>;
  }> => {
    const response = await api.get(`/advanced/exchanges/order-books/${symbol}`);
    return response.data;
  },

  getMarketSummary: async (): Promise<{
    total_exchanges: number;
    active_symbols: number;
    total_volume: number;
    arbitrage_opportunities: number;
    last_updated: string;
  }> => {
    const response = await api.get('/advanced/exchanges/market-summary');
    return response.data;
  },

  // Real-time Features
  createPriceAlert: async (
    symbol: string,
    condition: 'above' | 'below',
    threshold: number
  ): Promise<{
    alert_id: string;
    message: string;
  }> => {
    const response = await api.post('/advanced/alerts/price', {
      symbol,
      condition,
      threshold
    });
    return response.data;
  },

  getLiveOrderBook: async (symbol: string): Promise<OrderBook> => {
    const response = await api.get(`/advanced/orderbook/${symbol}`);
    return response.data;
  },

  getPriceHistory: async (symbol: string, limit: number = 100): Promise<{
    symbol: string;
    history: Array<{
      timestamp: string;
      price: number;
      volume: number;
    }>;
    count: number;
  }> => {
    const response = await api.get(`/advanced/price-history/${symbol}`, {
      params: { limit }
    });
    return response.data;
  },

  // System Control (Admin only)
  startAdvancedFeatures: async (): Promise<{
    message: string;
    features: string[];
  }> => {
    const response = await api.post('/advanced/system/start-advanced-features');
    return response.data;
  },

  stopAdvancedFeatures: async (): Promise<{
    message: string;
  }> => {
    const response = await api.post('/advanced/system/stop-advanced-features');
    return response.data;
  },

  // WebSocket connection helpers
  createWebSocketConnection: (
    endpoint: 'prices' | 'orderbook',
    symbols: string[],
    userId: number,
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: (event: CloseEvent) => void
  ): WebSocket => {
    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'}/api/v1/advanced/ws/${endpoint}`;
    const symbolsParam = symbols.join(',');
    const fullUrl = `${wsUrl}?symbols=${symbolsParam}&user_id=${userId}`;
    
    const ws = new WebSocket(fullUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    if (onError) {
      ws.onerror = onError;
    }
    
    if (onClose) {
      ws.onclose = onClose;
    }
    
    return ws;
  },
};