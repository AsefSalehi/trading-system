from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(
        Integer, ForeignKey("cryptocurrencies.id"), nullable=False
    )

    # Risk metrics
    volatility_score = Column(Float, nullable=False)  # 0-100 scale
    liquidity_score = Column(Float, nullable=False)  # 0-100 scale
    market_cap_score = Column(Float, nullable=False)  # 0-100 scale
    sentiment_score = Column(Float, nullable=True)  # -100 to 100 scale
    technical_score = Column(Float, nullable=False)  # 0-100 scale

    # Composite scores
    overall_risk_score = Column(Float, nullable=False)  # 0-100 scale (higher = riskier)
    confidence_interval = Column(Float, nullable=False)  # 0-1 scale

    # Metadata
    model_version = Column(String, nullable=False)
    calculation_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    data_window_days = Column(Integer, nullable=False, default=30)

    # Additional data
    risk_factors = Column(JSON, nullable=True)  # Store detailed risk factors
    recommendations = Column(Text, nullable=True)

    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="risk_scores")

    def __repr__(self):
        return f"<RiskScore(id={self.id}, crypto_id={self.cryptocurrency_id}, score={self.overall_risk_score})>"


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(
        Integer, ForeignKey("cryptocurrencies.id"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # None for system-wide alerts

    alert_type = Column(
        String, nullable=False
    )  # 'volatility', 'liquidity', 'sentiment', etc.
    severity = Column(String, nullable=False)  # 'low', 'medium', 'high', 'critical'
    threshold_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    is_active = Column(String, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    cryptocurrency = relationship("Cryptocurrency")
    user = relationship("User")

    def __repr__(self):
        return f"<RiskAlert(id={self.id}, type={self.alert_type}, severity={self.severity})>"
