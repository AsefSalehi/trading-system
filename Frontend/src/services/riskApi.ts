import api from './api';
import type { 
  RiskAssessment, 
  RiskMetrics, 
  RiskAlert 
} from '../types/risk';

export const riskApi = {
  // Risk assessment
  getRiskAssessment: async (userId?: string): Promise<RiskAssessment> => {
    const url = userId ? `/risk/assessment/${userId}` : '/risk/assessment';
    const response = await api.get(url);
    return response.data;
  },

  createRiskAssessment: async (userId?: string): Promise<RiskAssessment> => {
    const url = userId ? `/risk/assessment/${userId}` : '/risk/assessment';
    const response = await api.post(url);
    return response.data;
  },

  // Risk metrics
  getRiskMetrics: async (userId?: string): Promise<RiskMetrics> => {
    const url = userId ? `/risk/metrics/${userId}` : '/risk/metrics';
    const response = await api.get(url);
    return response.data;
  },

  // Risk alerts
  getRiskAlerts: async (params?: {
    limit?: number;
    severity?: string;
    acknowledged?: boolean;
  }): Promise<RiskAlert[]> => {
    const response = await api.get('/risk/alerts', { params });
    return response.data;
  },

  acknowledgeAlert: async (alertId: string): Promise<{ message: string }> => {
    const response = await api.post(`/risk/alerts/${alertId}/acknowledge`);
    return response.data;
  },

  // Portfolio risk analysis
  analyzePortfolioRisk: async (userId?: string): Promise<{
    risk_score: number;
    risk_level: string;
    recommendations: string[];
  }> => {
    const url = userId ? `/risk/portfolio-analysis/${userId}` : '/risk/portfolio-analysis';
    const response = await api.post(url);
    return response.data;
  },
};