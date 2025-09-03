import api from './api';

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

export const riskApi = {
  // Risk assessment - Using correct backend endpoints
  assessCryptocurrencyRisk: async (request: RiskAssessmentRequest): Promise<RiskScore[]> => {
    const response = await api.post('/risk/assess', request);
    return response.data;
  },

  getRiskScore: async (cryptoId: number, latest: boolean = true): Promise<RiskScore> => {
    const response = await api.get(`/risk/scores/${cryptoId}`, {
      params: { latest }
    });
    return response.data;
  },

  getRiskScores: async (params?: {
    skip?: number;
    limit?: number;
    crypto_id?: number;
    min_risk_score?: number;
    max_risk_score?: number;
  }): Promise<RiskScore[]> => {
    const response = await api.get('/risk/scores', { params });
    return response.data;
  },

  // Risk alerts - Using correct backend endpoints
  createRiskAlert: async (alertData: RiskAlertCreate): Promise<RiskAlert> => {
    const response = await api.post('/risk/alerts', alertData);
    return response.data;
  },

  getRiskAlerts: async (params?: {
    crypto_id?: number;
    severity?: string;
    alert_type?: string;
    user_specific?: boolean;
  }): Promise<RiskAlert[]> => {
    const response = await api.get('/risk/alerts', { params });
    return response.data;
  },

  resolveRiskAlert: async (alertId: number): Promise<{ message: string }> => {
    const response = await api.put(`/risk/alerts/${alertId}/resolve`);
    return response.data;
  },

  // Risk dashboard
  getRiskDashboard: async (): Promise<{
    high_risk_cryptocurrencies: RiskScore[];
    active_alerts_count: number;
    alert_counts_by_severity: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
    recent_alerts: RiskAlert[];
  }> => {
    const response = await api.get('/risk/dashboard');
    return response.data;
  },

  // Legacy methods for backward compatibility with existing components
  acknowledgeAlert: async (alertId: string | number): Promise<{ message: string }> => {
    const id = typeof alertId === 'string' ? parseInt(alertId) : alertId;
    return riskApi.resolveRiskAlert(id);
  },

  getRiskAssessment: async (): Promise<any> => {
    // This is a legacy method - redirect to dashboard
    return riskApi.getRiskDashboard();
  },

  getRiskMetrics: async (): Promise<any> => {
    // This is a legacy method - return empty metrics for now
    return {
      portfolio_concentration: 0,
      volatility_exposure: 0,
      liquidity_risk: 0,
      correlation_risk: 0,
      overall_risk_score: 0,
    };
  },

  createRiskAssessment: async (): Promise<any> => {
    // This is a legacy method - return empty assessment
    return {
      user_id: "1",
      risk_score: 0,
      risk_level: "LOW",
      factors: [],
      recommendations: [],
      created_at: new Date().toISOString(),
    };
  },

  analyzePortfolioRisk: async (): Promise<any> => {
    // This is a legacy method - return basic analysis
    return {
      risk_score: 0,
      risk_level: "LOW",
      recommendations: ["No specific risks detected"],
    };
  },
};
