export interface RiskScore {
  id: number;
  cryptocurrency_id: number;
  overall_risk_score: number;
  volatility_score: number;
  liquidity_score: number;
  market_cap_score: number;
  volume_score: number;
  price_change_score: number;
  technical_score: number;
  sentiment_score: number;
  created_at: string;
}

export interface RiskAlert {
  id: number;
  cryptocurrency_id: number;
  user_id?: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  threshold_value?: number;
  current_value?: number;
  is_active: boolean;
  created_at: string;
  resolved_at?: string;
}

export interface RiskAssessmentRequest {
  cryptocurrency_ids: number[];
  window_days: number;
}

export interface RiskAlertCreate {
  cryptocurrency_id: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  threshold_value?: number;
  current_value?: number;
  user_specific: boolean;
}

// Legacy interfaces for backward compatibility
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