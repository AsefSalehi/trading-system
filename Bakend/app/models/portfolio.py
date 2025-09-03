from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Portfolio(Base):
    """Portfolio model for risk management"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_value = Column(Float, default=0.0)
    target_risk_level = Column(Float, default=50.0)  # 0-100 scale
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    risk_analyses = relationship("PortfolioRiskAnalysis", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioHolding(Base):
    """Individual cryptocurrency holdings in a portfolio"""
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    average_buy_price = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    weight_percentage = Column(Float, default=0.0)  # Percentage of total portfolio
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    cryptocurrency = relationship("Cryptocurrency")


class PortfolioRiskAnalysis(Base):
    """Portfolio risk analysis results"""
    __tablename__ = "portfolio_risk_analyses"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    overall_risk_score = Column(Float, nullable=False)  # 0-100 scale
    volatility_score = Column(Float, nullable=False)
    concentration_risk = Column(Float, nullable=False)
    correlation_risk = Column(Float, nullable=False)
    liquidity_risk = Column(Float, nullable=False)
    var_95 = Column(Float, nullable=True)  # Value at Risk (95% confidence)
    expected_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="risk_analyses")



class RebalanceRecommendation(Base):
    """Portfolio rebalancing recommendations"""
    __tablename__ = "rebalance_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    recommendation_type = Column(String(50), nullable=False)  # 'reduce_risk', 'increase_diversification'
    current_allocation = Column(JSON, nullable=False)
    recommended_allocation = Column(JSON, nullable=False)
    expected_risk_reduction = Column(Float, nullable=True)
    expected_return_impact = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # 'low', 'medium', 'high'
    is_implemented = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    implemented_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    portfolio = relationship("Portfolio")
