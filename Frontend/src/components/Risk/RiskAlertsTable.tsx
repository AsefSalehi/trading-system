import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { riskApi } from '../../services/riskApi';
import type { RiskAlert } from '../../types/risk';
import { AlertTriangle, CheckCircle, Clock, Shield } from 'lucide-react';

interface RiskAlertsTableProps {
  alerts: RiskAlert[];
}

export const RiskAlertsTable: React.FC<RiskAlertsTableProps> = ({ alerts }) => {
  const queryClient = useQueryClient();

  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: string) => riskApi.acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-alerts'] });
    },
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'LOW':
        return 'text-blue-600 bg-blue-50';
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-50';
      case 'HIGH':
        return 'text-orange-600 bg-orange-50';
      case 'CRITICAL':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'LOW':
        return <Shield className="h-4 w-4" />;
      case 'MEDIUM':
        return <Clock className="h-4 w-4" />;
      case 'HIGH':
      case 'CRITICAL':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Shield className="h-4 w-4" />;
    }
  };

  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case 'PORTFOLIO_RISK':
        return 'Portfolio Risk';
      case 'POSITION_SIZE':
        return 'Position Size';
      case 'VOLATILITY':
        return 'Volatility';
      case 'CORRELATION':
        return 'Correlation';
      default:
        return type;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleAcknowledge = (alertId: string) => {
    acknowledgeMutation.mutate(alertId);
  };

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <AlertTriangle className="h-6 w-6 text-orange-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-900">Risk Alerts</h2>
        <span className="ml-2 text-sm text-gray-500">
          ({alerts.filter(alert => !alert.acknowledged).length} unacknowledged)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Message
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Triggered
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {alerts.map((alert) => (
              <tr 
                key={alert.id} 
                className={`hover:bg-gray-50 ${!alert.acknowledged ? 'bg-yellow-50' : ''}`}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {getAlertTypeLabel(alert.alert_type)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                    {getSeverityIcon(alert.severity)}
                    <span className="ml-1">{alert.severity}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                  <div className="truncate" title={alert.message}>
                    {alert.message}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(alert.triggered_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {alert.acknowledged ? (
                    <div className="inline-flex items-center text-green-600">
                      <CheckCircle className="h-4 w-4 mr-1" />
                      <span className="text-xs">Acknowledged</span>
                    </div>
                  ) : (
                    <div className="inline-flex items-center text-orange-600">
                      <Clock className="h-4 w-4 mr-1" />
                      <span className="text-xs">Pending</span>
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {!alert.acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      disabled={acknowledgeMutation.isPending}
                      className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                    >
                      Acknowledge
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Total Alerts:</span>
            <span className="font-semibold">{alerts.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Unacknowledged:</span>
            <span className="font-semibold text-orange-600">
              {alerts.filter(alert => !alert.acknowledged).length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Critical:</span>
            <span className="font-semibold text-red-600">
              {alerts.filter(alert => alert.severity === 'CRITICAL').length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">High:</span>
            <span className="font-semibold text-orange-600">
              {alerts.filter(alert => alert.severity === 'HIGH').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};