from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Risk Score Schemas
class RiskScoreBase(BaseModel):
    cryptocurrency_id: int
    volatility_score: float = Field(..., ge=0, le=100)
    liquidity_score: float = Field(..., ge=0, le=100)
    market_cap_score: float = Field(..., ge=0, le=100)
    sentiment_score: Optional[float] = Field(None, ge=-100, le=100)
    technical_score: float = Field(..., ge=0, le=100)
    overall_risk_score: float = Field(..., ge=0, le=100)
    confidence_interval: float = Field(..., ge=0, le=1)
    model_version: str
    data_window_days: int = Field(..., ge=1, le=365)
    risk_factors: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None


class RiskScore(RiskScoreBase):
    id: int
    calculation_timestamp: datetime

    class Config:
        from_attributes = True


# Risk Alert Schemas
class RiskAlertBase(BaseModel):
    cryptocurrency_id: int
    alert_type: str = Field(
        ..., description="Type of alert (volatility, liquidity, sentiment, etc.)"
    )
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    threshold_value: float
    current_value: float
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)


class RiskAlertCreate(RiskAlertBase):
    user_specific: bool = Field(
        False, description="Whether this alert is user-specific"
    )


class RiskAlert(RiskAlertBase):
    id: int
    user_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Risk Assessment Request
class RiskAssessmentRequest(BaseModel):
    cryptocurrency_ids: Optional[List[int]] = Field(
        None, description="List of crypto IDs to assess. If None, assesses top 100"
    )
    window_days: int = Field(30, ge=7, le=365, description="Number of days to analyze")


# Risk Dashboard Response
class RiskDashboard(BaseModel):
    high_risk_cryptocurrencies: List[RiskScore]
    active_alerts_count: int
    alert_counts_by_severity: Dict[str, int]
    recent_alerts: List[RiskAlert]


# Portfolio Risk Schemas (for future portfolio management)
class PortfolioRiskBase(BaseModel):
    user_id: int
    total_value: float
    risk_score: float = Field(..., ge=0, le=100)
    diversification_score: float = Field(..., ge=0, le=100)
    volatility: float
    var_95: float  # Value at Risk at 95% confidence
    max_drawdown: float


class PortfolioRisk(PortfolioRiskBase):
    id: int
    calculation_timestamp: datetime
    positions: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
