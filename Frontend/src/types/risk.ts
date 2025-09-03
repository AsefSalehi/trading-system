export interface RiskAssessment {
  user_id: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  factors: RiskFactor[];
  recommendations: string[];
  created_at: string;
}

export interface RiskFactor {
  factor_type: string;
  value: number;
  weight: number;
  description: string;
}

export interface RiskMetrics {
  portfolio_concentration: number;
  volatility_exposure: number;
  liquidity_risk: number;
  correlation_risk: number;
  overall_risk_score: number;
}

export interface RiskAlert {
  id: string;
  user_id: string;
  alert_type: 'PORTFOLIO_RISK' | 'POSITION_SIZE' | 'VOLATILITY' | 'CORRELATION';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  triggered_at: string;
  acknowledged: boolean;
}