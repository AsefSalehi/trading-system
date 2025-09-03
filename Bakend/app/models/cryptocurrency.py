from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)

    # Market data
    current_price = Column(DECIMAL(20, 8), nullable=True)
    market_cap = Column(DECIMAL(20, 2), nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    total_volume = Column(DECIMAL(20, 2), nullable=True)
    circulating_supply = Column(DECIMAL(20, 2), nullable=True)
    total_supply = Column(DECIMAL(20, 2), nullable=True)
    max_supply = Column(DECIMAL(20, 2), nullable=True)

    # Price changes
    price_change_24h = Column(DECIMAL(20, 8), nullable=True)
    price_change_percentage_24h = Column(DECIMAL(8, 4), nullable=True)
    price_change_percentage_7d = Column(DECIMAL(8, 4), nullable=True)
    price_change_percentage_30d = Column(DECIMAL(8, 4), nullable=True)

    # Technical data
    ath = Column(DECIMAL(20, 8), nullable=True)  # All-time high
    ath_date = Column(DateTime, nullable=True)
    atl = Column(DECIMAL(20, 8), nullable=True)  # All-time low
    atl_date = Column(DateTime, nullable=True)

    # Metadata
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    whitepaper = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    risk_scores = relationship("RiskScore", back_populates="cryptocurrency")

    # Database indexes for query optimization
    __table_args__ = (
        Index("idx_market_cap_rank", "market_cap_rank"),
        Index("idx_market_cap", "market_cap"),
        Index("idx_total_volume", "total_volume"),
        Index("idx_price_change_24h", "price_change_percentage_24h"),
        Index("idx_last_updated", "last_updated"),
        Index("idx_active_coins", "is_active", "market_cap_rank"),
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)

    # Price data
    price = Column(DECIMAL(20, 8), nullable=False)
    market_cap = Column(DECIMAL(20, 2), nullable=True)
    total_volume = Column(DECIMAL(20, 2), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    # Database indexes for query optimization
    __table_args__ = (
        Index("idx_crypto_timestamp", "cryptocurrency_id", "timestamp"),
        Index("idx_symbol_timestamp", "symbol", "timestamp"),
        Index("idx_price_history_lookup", "symbol", "timestamp", "price"),
    )
