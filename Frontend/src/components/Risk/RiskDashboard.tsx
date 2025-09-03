import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskApi } from '../../services/riskApi';
import { RiskMetricsCard } from './RiskMetricsCard';
import { RiskAssessmentCard } from './RiskAssessmentCard';
import { RiskAlertsTable } from './RiskAlertsTable';
import { Shield, RefreshCw, AlertTriangle } from 'lucide-react';

export const RiskDashboard: React.FC = () => {
  const queryClient = useQueryClient();

  // Fetch risk assessment
  const { data: riskAssessment, isLoading: assessmentLoading } = useQuery({
    queryKey: ['risk-assessment'],
    queryFn: () => riskApi.getRiskAssessment(),
    retry: false,
  });

  // Fetch risk metrics
  const { data: riskMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['risk-metrics'],
    queryFn: () => riskApi.getRiskMetrics(),
    retry: false,
  });

  // Fetch risk alerts
  const { data: riskAlerts } = useQuery({
    queryKey: ['risk-alerts'],
    queryFn: () => riskApi.getRiskAlerts({ limit: 20 }),
  });

  // Create risk assessment mutation
  const createAssessmentMutation = useMutation({
    mutationFn: () => riskApi.createRiskAssessment(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-assessment'] });
      queryClient.invalidateQueries({ queryKey: ['risk-metrics'] });
    },
  });

  // Analyze portfolio risk mutation
  const analyzeRiskMutation = useMutation({
    mutationFn: () => riskApi.analyzePortfolioRisk(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-assessment'] });
      queryClient.invalidateQueries({ queryKey: ['risk-metrics'] });
      queryClient.invalidateQueries({ queryKey: ['risk-alerts'] });
    },
  });

  const handleCreateAssessment = () => {
    createAssessmentMutation.mutate();
  };

  const handleAnalyzeRisk = () => {
    analyzeRiskMutation.mutate();
  };

  const isLoading = assessmentLoading || metricsLoading;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Shield className="h-8 w-8 text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Risk Analysis</h1>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleAnalyzeRisk}
            disabled={analyzeRiskMutation.isPending}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${analyzeRiskMutation.isPending ? 'animate-spin' : ''}`} />
            Analyze Portfolio Risk
          </button>
          {!riskAssessment && (
            <button
              onClick={handleCreateAssessment}
              disabled={createAssessmentMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <Shield className="h-4 w-4 mr-2" />
              {createAssessmentMutation.isPending ? 'Creating...' : 'Create Assessment'}
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Risk Metrics */}
          {riskMetrics && <RiskMetricsCard metrics={riskMetrics} />}

          {/* Risk Assessment */}
          {riskAssessment ? (
            <RiskAssessmentCard assessment={riskAssessment} />
          ) : (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <AlertTriangle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Risk Assessment Available</h3>
              <p className="text-gray-600 mb-6">
                Create a risk assessment to analyze your portfolio's risk profile and get personalized recommendations.
              </p>
              <button
                onClick={handleCreateAssessment}
                disabled={createAssessmentMutation.isPending}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <Shield className="h-5 w-5 mr-2" />
                {createAssessmentMutation.isPending ? 'Creating...' : 'Create Risk Assessment'}
              </button>
            </div>
          )}

          {/* Risk Alerts */}
          {riskAlerts && riskAlerts.length > 0 && (
            <RiskAlertsTable alerts={riskAlerts} />
          )}
        </>
      )}
    </div>
  );
};