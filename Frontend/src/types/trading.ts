export interface Wallet {
  id: string;
  user_id: string;
  usd_balance: number;
  total_portfolio_value: number;
  total_profit_loss: number;
  total_trades: number;
  win_rate: number;
  created_at: string;
}

export interface TradeRequest {
  symbol: string;
  amount: number;
}

export interface TradeResponse {
  success: boolean;
  message: string;
  transaction_id?: string;
  executed_price?: number;
  executed_quantity?: number;
  total_amount?: number;
  fee?: number;
  new_balance?: number;
}

export interface Transaction {
  id: string;
  transaction_type: 'BUY' | 'SELL' | 'DEPOSIT' | 'WITHDRAWAL';
  symbol: string;
  quantity: number;
  price: number;
  total_amount: number;
  fee: number;
  realized_pnl: number;
  realized_pnl_percentage: number;
  created_at: string;
}

export interface Holding {
  id: string;
  symbol: string;
  quantity: number;
  average_buy_price: number;
  current_price: number;
  total_cost: number;
  current_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percentage: number;
  first_purchase_at: string;
}

export interface PortfolioSummary {
  wallet: Wallet;
  holdings: Holding[];
  total_invested: number;
  total_current_value: number;
  total_unrealized_pnl: number;
  total_unrealized_pnl_percentage: number;
  best_performer?: {
    symbol: string;
    pnl_percentage: number;
  };
  worst_performer?: {
    symbol: string;
    pnl_percentage: number;
  };
}