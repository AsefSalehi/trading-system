import React from 'react';
import type { PortfolioSummary as PortfolioSummaryType } from '../../types/trading';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Award,
  AlertTriangle
} from 'lucide-react';

interface PortfolioSummaryProps {
  portfolio: PortfolioSummaryType;
}

export const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ portfolio }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (percentage: number | undefined) => {
    if (percentage === undefined || percentage === null || isNaN(percentage)) {
      return '0.00%';
    }
    return `${percentage >= 0 ? '+' : ''}${percentage.toFixed(2)}%`;
  };

  const safeNumber = (value: number | undefined): number => {
    return value ?? 0;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total Invested */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center">
          <DollarSign className="h-8 w-8 text-blue-600" />
          <div className="ml-3">
            <p className="text-sm font-medium text-blue-600">Total Invested</p>
            <p className="text-2xl font-bold text-blue-900">
              {formatCurrency(safeNumber(portfolio.total_invested))}
            </p>
          </div>
        </div>
      </div>

      {/* Current Value */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center">
          <Target className="h-8 w-8 text-purple-600" />
          <div className="ml-3">
            <p className="text-sm font-medium text-purple-600">Current Value</p>
            <p className="text-2xl font-bold text-purple-900">
              {formatCurrency(safeNumber(portfolio.total_current_value))}
            </p>
          </div>
        </div>
      </div>

      {/* Unrealized P&L */}
      <div className={`bg-white rounded-lg shadow-md p-6 ${
        safeNumber(portfolio.total_unrealized_pnl) >= 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'
      }`}>
        <div className="flex items-center">
          {safeNumber(portfolio.total_unrealized_pnl) >= 0 ? (
            <TrendingUp className="h-8 w-8 text-green-600" />
          ) : (
            <TrendingDown className="h-8 w-8 text-red-600" />
          )}
          <div className="ml-3">
            <p className={`text-sm font-medium ${
              safeNumber(portfolio.total_unrealized_pnl) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              Unrealized P&L
            </p>
            <p className={`text-2xl font-bold ${
              safeNumber(portfolio.total_unrealized_pnl) >= 0 ? 'text-green-900' : 'text-red-900'
            }`}>
              {formatCurrency(safeNumber(portfolio.total_unrealized_pnl))}
            </p>
            <p className={`text-sm ${
              safeNumber(portfolio.total_unrealized_pnl) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatPercentage(portfolio.total_unrealized_pnl_percentage)}
            </p>
          </div>
        </div>
      </div>

      {/* Cash Balance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center">
          <DollarSign className="h-8 w-8 text-gray-600" />
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-600">Cash Balance</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(safeNumber(portfolio.wallet?.usd_balance))}
            </p>
          </div>
        </div>
      </div>

      {/* Performance Highlights */}
      {(portfolio.best_performer || portfolio.worst_performer) && (
        <div className="md:col-span-2 lg:col-span-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Highlights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Best Performer */}
              {portfolio.best_performer && (
                <div className="flex items-center p-4 bg-green-50 rounded-lg">
                  <Award className="h-8 w-8 text-green-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-600">Best Performer</p>
                    <p className="text-lg font-bold text-green-900">
                      {portfolio.best_performer.symbol}
                    </p>
                    <p className="text-sm text-green-600">
                      +{safeNumber(portfolio.best_performer.pnl_percentage).toFixed(2)}%
                    </p>
                  </div>
                </div>
              )}

              {/* Worst Performer */}
              {portfolio.worst_performer && (
                <div className="flex items-center p-4 bg-red-50 rounded-lg">
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-600">Worst Performer</p>
                    <p className="text-lg font-bold text-red-900">
                      {portfolio.worst_performer.symbol}
                    </p>
                    <p className="text-sm text-red-600">
                      {safeNumber(portfolio.worst_performer.pnl_percentage).toFixed(2)}%
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
