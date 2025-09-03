from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class OrderType(str, enum.Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Balances
    usd_balance = Column(DECIMAL(20, 8), nullable=False, default=10000.00)  # Start with $10,000
    total_invested = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    total_profit_loss = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    
    # Portfolio metrics
    total_portfolio_value = Column(DECIMAL(20, 8), nullable=False, default=10000.00)
    daily_pnl = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)
    
    # Risk metrics
    max_drawdown = Column(DECIMAL(8, 4), nullable=False, default=0.00)  # Percentage
    win_rate = Column(DECIMAL(8, 4), nullable=False, default=0.00)  # Percentage
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    holdings = relationship("Holding", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")
    orders = relationship("Order", back_populates="wallet")

    def __repr__(self):
        return f"<Wallet(id={self.id}, user_id={self.user_id}, balance=${self.usd_balance})>"


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=False)
    
    # Position details
    symbol = Column(String(10), nullable=False, index=True)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    average_buy_price = Column(DECIMAL(20, 8), nullable=False)
    current_price = Column(DECIMAL(20, 8), nullable=True)
    
    # P&L calculations
    total_cost = Column(DECIMAL(20, 8), nullable=False)  # quantity * avg_buy_price
    current_value = Column(DECIMAL(20, 8), nullable=True)  # quantity * current_price
    unrealized_pnl = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    unrealized_pnl_percentage = Column(DECIMAL(8, 4), nullable=False, default=0.00)
    
    # Timestamps
    first_purchase_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="holdings")
    cryptocurrency = relationship("Cryptocurrency")

    def __repr__(self):
        return f"<Holding(id={self.id}, symbol={self.symbol}, qty={self.quantity})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=True)
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    symbol = Column(String(10), nullable=True, index=True)  # Null for USD deposits/withdrawals
    quantity = Column(DECIMAL(20, 8), nullable=True)
    price = Column(DECIMAL(20, 8), nullable=True)
    total_amount = Column(DECIMAL(20, 8), nullable=False)
    
    # Fees
    fee = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    fee_percentage = Column(DECIMAL(8, 4), nullable=False, default=0.1)  # 0.1% default fee
    
    # P&L for sells
    realized_pnl = Column(DECIMAL(20, 8), nullable=True)
    realized_pnl_percentage = Column(DECIMAL(8, 4), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    cryptocurrency = relationship("Cryptocurrency")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount=${self.total_amount})>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=False)
    
    # Order details
    order_type = Column(Enum(OrderType), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)  # BUY or SELL
    symbol = Column(String(10), nullable=False, index=True)
    
    # Quantities and prices
    quantity = Column(DECIMAL(20, 8), nullable=False)
    executed_quantity = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    price = Column(DECIMAL(20, 8), nullable=True)  # Null for market orders
    executed_price = Column(DECIMAL(20, 8), nullable=True)
    
    # Order management
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    total_amount = Column(DECIMAL(20, 8), nullable=False)
    fee = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    
    # Stop loss / Take profit
    stop_price = Column(DECIMAL(20, 8), nullable=True)
    trigger_price = Column(DECIMAL(20, 8), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="orders")
    cryptocurrency = relationship("Cryptocurrency")

    def __repr__(self):
        return f"<Order(id={self.id}, type={self.order_type}, symbol={self.symbol}, status={self.status})>"


class TradingSession(Base):
    __tablename__ = "trading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_name = Column(String(100), nullable=False)
    starting_balance = Column(DECIMAL(20, 8), nullable=False)
    current_balance = Column(DECIMAL(20, 8), nullable=False)
    
    # Performance metrics
    total_pnl = Column(DECIMAL(20, 8), nullable=False, default=0.00)
    total_pnl_percentage = Column(DECIMAL(8, 4), nullable=False, default=0.00)
    max_balance = Column(DECIMAL(20, 8), nullable=False)
    min_balance = Column(DECIMAL(20, 8), nullable=False)
    
    # Trading stats
    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)
    win_rate = Column(DECIMAL(8, 4), nullable=False, default=0.00)
    
    # Risk metrics
    max_drawdown = Column(DECIMAL(8, 4), nullable=False, default=0.00)
    sharpe_ratio = Column(DECIMAL(8, 4), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<TradingSession(id={self.id}, name={self.session_name}, pnl={self.total_pnl})>"