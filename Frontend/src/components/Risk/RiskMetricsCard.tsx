import React from 'react';
import type { RiskMetrics } from '../../types/risk';
import { Shield, TrendingUp, Droplets, GitBranch, AlertCircle } from 'lucide-react';

interface RiskMetricsCardProps {
  metrics: RiskMetrics;
}

export const RiskMetricsCard: React.FC<RiskMetricsCardProps> = ({ metrics }) => {
  const getRiskColor = (score: number) => {
    if (score <= 0.3) return 'text-green-600';
    if (score <= 0.6) return 'text-yellow-600';
    if (score <= 0.8) return 'text-orange-600';
    return 'text-red-600';
  };

  const getRiskBgColor = (score: number) => {
    if (score <= 0.3) return 'bg-green-50 border-green-200';
    if (score <= 0.6) return 'bg-yellow-50 border-yellow-200';
    if (score <= 0.8) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  const getRiskLevel = (score: number) => {
    if (score <= 0.3) return 'Low';
    if (score <= 0.6) return 'Medium';
    if (score <= 0.8) return 'High';
    return 'Critical';
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const riskMetrics = [
    {
      label: 'Portfolio Concentration',
      value: metrics.portfolio_concentration,
      icon: GitBranch,
      description: 'Measures how concentrated your portfolio is in specific assets',
    },
    {
      label: 'Volatility Exposure',
      value: metrics.volatility_exposure,
      icon: TrendingUp,
      description: 'Exposure to price volatility across your holdings',
    },
    {
      label: 'Liquidity Risk',
      value: metrics.liquidity_risk,
      icon: Droplets,
      description: 'Risk of not being able to quickly sell your positions',
    },
    {
      label: 'Correlation Risk',
      value: metrics.correlation_risk,
      icon: GitBranch,
      description: 'Risk from assets moving in the same direction',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <Shield className="h-6 w-6 text-blue-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-900">Risk Metrics</h2>
      </div>

      {/* Overall Risk Score */}
      <div className={`rounded-lg border-2 p-6 mb-6 ${getRiskBgColor(metrics.overall_risk_score)}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Overall Risk Score</h3>
            <p className="text-sm text-gray-600 mt-1">
              Comprehensive risk assessment of your portfolio
            </p>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getRiskColor(metrics.overall_risk_score)}`}>
              {formatPercentage(metrics.overall_risk_score)}
            </div>
            <div className={`text-sm font-medium ${getRiskColor(metrics.overall_risk_score)}`}>
              {getRiskLevel(metrics.overall_risk_score)} Risk
            </div>
          </div>
        </div>
      </div>

      {/* Individual Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {riskMetrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div key={metric.label} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <Icon className="h-5 w-5 text-gray-600 mr-2" />
                  <div>
                    <h4 className="font-medium text-gray-900">{metric.label}</h4>
                    <p className="text-xs text-gray-500 mt-1">{metric.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-xl font-bold ${getRiskColor(metric.value)}`}>
                    {formatPercentage(metric.value)}
                  </div>
                  <div className={`text-xs font-medium ${getRiskColor(metric.value)}`}>
                    {getRiskLevel(metric.value)}
                  </div>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      metric.value <= 0.3 ? 'bg-green-500' :
                      metric.value <= 0.6 ? 'bg-yellow-500' :
                      metric.value <= 0.8 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(metric.value * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Risk Level Explanation */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Risk Level Guide</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2" />
                <span className="text-gray-600">Low (0-30%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2" />
                <span className="text-gray-600">Medium (30-60%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-orange-500 rounded-full mr-2" />
                <span className="text-gray-600">High (60-80%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-2" />
                <span className="text-gray-600">Critical (80-100%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};