import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { tradingApi } from '../../services/tradingApi';
import { PortfolioSummary } from './PortfolioSummary';
import { HoldingsTable } from './HoldingsTable';
import { PortfolioChart } from './PortfolioChart';
import { BarChart3 } from 'lucide-react';

export const PortfolioDashboard: React.FC = () => {
  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['portfolio'],
    queryFn: tradingApi.getPortfolioSummary,
    retry: false,
  });

  const { data: holdings } = useQuery({
    queryKey: ['holdings'],
    queryFn: tradingApi.getHoldings,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Portfolio Not Available</h2>
          <p className="text-gray-600">
            Please create a trading wallet first to view your portfolio.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Portfolio Overview</h1>
      </div>

      {/* Portfolio Summary */}
      {portfolio && <PortfolioSummary portfolio={portfolio} />}

      {/* Portfolio Chart */}
      {holdings && holdings.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Portfolio Allocation</h2>
          <PortfolioChart holdings={holdings} />
        </div>
      )}

      {/* Holdings Table */}
      <HoldingsTable holdings={holdings || []} />
    </div>
  );
};