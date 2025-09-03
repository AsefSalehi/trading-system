import React from 'react';
import type { RiskAssessment } from '../../types/risk';
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface RiskAssessmentCardProps {
  assessment: RiskAssessment;
}

export const RiskAssessmentCard: React.FC<RiskAssessmentCardProps> = ({ assessment }) => {
  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'HIGH':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'CRITICAL':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'LOW':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'MEDIUM':
        return <Info className="h-6 w-6 text-yellow-600" />;
      case 'HIGH':
      case 'CRITICAL':
        return <AlertTriangle className="h-6 w-6 text-red-600" />;
      default:
        return <Shield className="h-6 w-6 text-gray-600" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Shield className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Risk Assessment</h2>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {formatDate(assessment.created_at)}
        </div>
      </div>

      {/* Risk Level Summary */}
      <div className={`rounded-lg border-2 p-6 mb-6 ${getRiskLevelColor(assessment.risk_level)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {getRiskIcon(assessment.risk_level)}
            <div className="ml-3">
              <h3 className="text-lg font-semibold">
                {assessment.risk_level} Risk Level
              </h3>
              <p className="text-sm opacity-75">
                Risk Score: {assessment.risk_score.toFixed(2)}/100
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">
              {assessment.risk_score.toFixed(0)}
            </div>
            <div className="text-sm opacity-75">out of 100</div>
          </div>
        </div>
      </div>

      {/* Risk Factors */}
      {assessment.factors && assessment.factors.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Factors</h3>
          <div className="space-y-3">
            {assessment.factors.map((factor, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{factor.factor_type}</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">Weight: {(factor.weight * 100).toFixed(0)}%</span>
                    <span className="text-sm font-medium text-gray-900">
                      Value: {factor.value.toFixed(2)}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{factor.description}</p>
                
                {/* Factor Progress Bar */}
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        factor.value <= 0.3 ? 'bg-green-500' :
                        factor.value <= 0.6 ? 'bg-yellow-500' :
                        factor.value <= 0.8 ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(factor.value * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {assessment.recommendations && assessment.recommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <ul className="space-y-2">
              {assessment.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-blue-800">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Risk Level Explanation */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Understanding Your Risk Level</h4>
        <div className="text-sm text-gray-600">
          {assessment.risk_level === 'LOW' && (
            <p>Your portfolio has a low risk profile. This suggests good diversification and conservative positioning. Continue monitoring and consider gradual expansion if your risk tolerance allows.</p>
          )}
          {assessment.risk_level === 'MEDIUM' && (
            <p>Your portfolio has a moderate risk profile. This is generally acceptable for most investors. Consider reviewing your positions and ensuring proper diversification across different asset types.</p>
          )}
          {assessment.risk_level === 'HIGH' && (
            <p>Your portfolio has a high risk profile. Consider reducing position sizes, diversifying across more assets, or taking profits on highly volatile positions to manage risk.</p>
          )}
          {assessment.risk_level === 'CRITICAL' && (
            <p>Your portfolio has a critical risk level. Immediate action is recommended to reduce risk exposure. Consider significant position reductions, diversification, or consultation with a financial advisor.</p>
          )}
        </div>
      </div>
    </div>
  );
};