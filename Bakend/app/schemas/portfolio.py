from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PortfolioHoldingBase(BaseModel):
    cryptocurrency_id: int
    quantity: float = Field(..., gt=0)
    average_buy_price: float = Field(..., gt=0)


class PortfolioHoldingCreate(PortfolioHoldingBase):
    pass


class PortfolioHoldingUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    average_buy_price: Optional[float] = Field(None, gt=0)


class PortfolioHolding(PortfolioHoldingBase):
    id: int
    portfolio_id: int
    current_value: float
    weight_percentage: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_risk_level: float = Field(50.0, ge=0, le=100)


class PortfolioCreate(PortfolioBase):
    holdings: Optional[List[PortfolioHoldingCreate]] = []


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_risk_level: Optional[float] = Field(None, ge=0, le=100)


class Portfolio(PortfolioBase):
    id: int
    user_id: int
    total_value: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    holdings: List[PortfolioHolding] = []

    class Config:
        from_attributes = True


class PortfolioRiskAnalysis(BaseModel):
    id: int
    portfolio_id: int
    overall_risk_score: float
    volatility_score: float
    concentration_risk: float
    correlation_risk: float
    liquidity_risk: float
    var_95: Optional[float]
    expected_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    risk_factors: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    analysis_date: datetime

    class Config:
        from_attributes = True


class RiskAlertBase(BaseModel):
    alert_type: str
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None


class RiskAlertCreate(RiskAlertBase):
    portfolio_id: Optional[int] = None
    cryptocurrency_id: Optional[int] = None
    user_specific: bool = False


class RiskAlert(RiskAlertBase):
    id: int
    portfolio_id: Optional[int]
    cryptocurrency_id: Optional[int]
    user_id: Optional[int]
    is_active: bool
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class PortfolioRecommendation(BaseModel):
    id: int
    portfolio_id: int
    recommendation_type: str
    current_allocation: Dict[str, Any]
    recommended_allocation: Dict[str, Any]
    expected_risk_reduction: Optional[float]
    expected_return_impact: Optional[float]
    reasoning: str
    priority: str
    is_implemented: bool
    created_at: datetime
    implemented_at: Optional[datetime]

    class Config:
        from_attributes = True


class RebalancePlan(BaseModel):
    portfolio_id: int
    current_risk_score: float
    target_risk_score: float
    actions: List[Dict[str, Any]]
    expected_risk_reduction: float
    estimated_cost: float
    reasoning: str


class PortfolioDashboard(BaseModel):
    portfolio: Portfolio
    risk_analysis: Optional[PortfolioRiskAnalysis]
    active_alerts: List[RiskAlert]
    recent_recommendations: List[PortfolioRecommendation]
    performance_metrics: Dict[str, Any]