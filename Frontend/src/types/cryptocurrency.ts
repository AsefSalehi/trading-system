export interface Cryptocurrency {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  total_volume: number;
  price_change_percentage_24h: number;
  price_change_percentage_7d?: number;
  price_change_percentage_30d?: number;
  last_updated: string;
  image?: string;
}

export interface CryptocurrencyList {
  items: Cryptocurrency[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PriceHistory {
  timestamp: string;
  price: number;
  volume?: number;
  market_cap?: number;
}

export interface PriceHistoryList {
  symbol: string;
  items: PriceHistory[];
  total: number;
}

export interface DataUpdateResponse {
  message: string;
  updated_count: number;
  created_count: number;
  timestamp: string;
}