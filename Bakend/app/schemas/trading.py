from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Wallet Schemas
class WalletBase(BaseModel):
    usd_balance: float
    total_portfolio_value: float
    total_profit_loss: float


class WalletResponse(WalletBase):
    id: int
    user_id: int
    total_trades: int
    win_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


# Trading Schemas
class TradeRequest(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    amount: float = Field(..., gt=0, description="Amount in USD for buy orders, quantity for sell orders")


class TradeResponse(BaseModel):
    status: str
    transaction_id: int
    symbol: str
    quantity: float
    price: float
    total_amount: float
    fee: float
    realized_pnl: Optional[float] = None
    realized_pnl_percentage: Optional[float] = None
    remaining_balance: float


# Transaction Schemas
class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    symbol: Optional[str]
    quantity: float
    price: float
    total_amount: float
    fee: float
    realized_pnl: float
    realized_pnl_percentage: float
    created_at: datetime


# Holding Schemas
class HoldingResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    average_buy_price: float
    current_price: float
    total_cost: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_percentage: float
    first_purchase_at: datetime


# Portfolio Summary
class PortfolioSummary(BaseModel):
    # Portfolio values
    total_portfolio_value: float
    usd_balance: float
    total_unrealized_pnl: float
    total_realized_pnl: float
    daily_pnl: float
    total_pnl: float
    total_pnl_percentage: float

    # Risk metrics
    max_drawdown: float
    win_rate: float

    # Trading stats
    total_trades: int
    winning_trades: int
    losing_trades: int

    # Holdings and transactions
    holdings: List[HoldingResponse]
    recent_transactions: List[Dict[str, Any]]


# Order Schemas (for future limit orders)
class OrderRequest(BaseModel):
    symbol: str
    order_type: str = Field(..., pattern="^(market|limit|stop_loss|take_profit)$")
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    stop_price: Optional[float] = Field(None, gt=0)


class OrderResponse(BaseModel):
    id: int
    symbol: str
    order_type: str
    transaction_type: str
    quantity: float
    executed_quantity: float
    price: Optional[float]
    executed_price: Optional[float]
    status: str
    total_amount: float
    fee: float
    created_at: datetime
    executed_at: Optional[datetime]


# Trading Session Schemas
class TradingSessionCreate(BaseModel):
    session_name: str = Field(..., max_length=100)
    starting_balance: float = Field(10000.0, gt=0)


class TradingSessionResponse(BaseModel):
    id: int
    session_name: str
    starting_balance: float
    current_balance: float
    total_pnl: float
    total_pnl_percentage: float
    max_balance: float
    min_balance: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown: float
    sharpe_ratio: Optional[float]
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


# Market Data Schemas
class MarketPrice(BaseModel):
    symbol: str
    price: float
    change_24h: float
    change_percentage_24h: float
    volume_24h: float
    market_cap: float
    last_updated: datetime


class TradingDashboard(BaseModel):
    portfolio_summary: PortfolioSummary
    market_prices: List[MarketPrice]
    top_gainers: List[MarketPrice]
    top_losers: List[MarketPrice]
    trending_coins: List[MarketPrice]
