import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tradingApi } from '../../services/tradingApi';
import { PortfolioSummary } from './PortfolioSummary';
import { HoldingsTable } from './HoldingsTable';
import { PortfolioChart } from './PortfolioChart';
import { BarChart3, Wallet, Plus, RefreshCw } from 'lucide-react';

export const PortfolioDashboard: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['portfolio'],
    queryFn: tradingApi.getPortfolioSummary,
    retry: false,
  });

  const { data: holdings } = useQuery({
    queryKey: ['holdings'],
    queryFn: tradingApi.getHoldings,
    retry: false,
  });

  // Create wallet mutation
  const createWalletMutation = useMutation({
    mutationFn: tradingApi.createWallet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      queryClient.invalidateQueries({ queryKey: ['holdings'] });
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
    },
  });

  // Update portfolio values mutation
  const updatePortfolioMutation = useMutation({
    mutationFn: tradingApi.updatePortfolioValues,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      queryClient.invalidateQueries({ queryKey: ['holdings'] });
    },
  });

  const handleCreateWallet = () => {
    createWalletMutation.mutate();
  };

  const handleUpdatePortfolio = () => {
    updatePortfolioMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="bg-white rounded-xl shadow-lg p-8 flex items-center space-x-4">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <span className="text-xl font-medium text-gray-700">Loading portfolio...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <Wallet className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Trading Wallet Found</h2>
          <p className="text-gray-600 mb-6">
            You need to create a trading wallet before you can view your portfolio.
          </p>
          <button
            onClick={handleCreateWallet}
            disabled={createWalletMutation.isPending}
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 font-medium shadow-lg hover:shadow-xl transition-all duration-200"
          >
            <Plus className="h-5 w-5 mr-2" />
            {createWalletMutation.isPending ? 'Creating...' : 'Create Trading Wallet'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Portfolio Overview
          </h1>
          <p className="text-gray-600 mt-1">Track your investments and performance</p>
        </div>
        <button
          onClick={handleUpdatePortfolio}
          disabled={updatePortfolioMutation.isPending}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 font-medium shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${updatePortfolioMutation.isPending ? 'animate-spin' : ''}`} />
          Update Prices
        </button>
      </div>

      {/* Portfolio Summary */}
      {portfolio && <PortfolioSummary portfolio={portfolio} />}

      {/* Portfolio Chart */}
      {holdings && holdings.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Portfolio Allocation</h2>
          <PortfolioChart holdings={holdings} />
        </div>
      )}

      {/* Holdings Table */}
      <HoldingsTable holdings={holdings || []} />

      {/* Empty State */}
      {portfolio && (!holdings || holdings.length === 0) && (
        <div className="bg-white rounded-xl shadow-lg p-8 text-center border border-gray-100">
          <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Holdings Yet</h3>
          <p className="text-gray-600 mb-4">
            Start trading to see your portfolio holdings and performance here.
          </p>
          <button
            onClick={() => window.location.hash = '#trading'}
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 font-medium shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Start Trading
          </button>
        </div>
      )}
    </div>
  );
};
