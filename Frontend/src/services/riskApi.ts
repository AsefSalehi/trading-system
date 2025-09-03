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
};