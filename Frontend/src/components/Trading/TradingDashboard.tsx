import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tradingApi } from '../../services/tradingApi';
import { cryptocurrencyApi } from '../../services/api';
import { TradingForm } from './TradingForm';
import { WalletInfo } from './WalletInfo';
import { TransactionHistory } from './TransactionHistory';
import { Wallet, Plus, RefreshCw } from 'lucide-react';

export const TradingDashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const queryClient = useQueryClient();

  // Fetch wallet data
  const { data: wallet, isLoading: walletLoading, error: walletError } = useQuery({
    queryKey: ['wallet'],
    queryFn: tradingApi.getWallet,
    retry: false,
  });

  // Fetch cryptocurrencies for trading
  const { data: cryptoList } = useQuery({
    queryKey: ['cryptocurrencies', { limit: 50 }],
    queryFn: () => cryptocurrencyApi.getCryptocurrencies({ limit: 50, sort_by: 'market_cap', order: 'desc' }),
  });

  // Create wallet mutation
  const createWalletMutation = useMutation({
    mutationFn: tradingApi.createWallet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
    },
  });

  // Update portfolio values mutation
  const updatePortfolioMutation = useMutation({
    mutationFn: tradingApi.updatePortfolioValues,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
      queryClient.invalidateQueries({ queryKey: ['holdings'] });
    },
  });

  const handleCreateWallet = () => {
    createWalletMutation.mutate();
  };

  const handleUpdatePortfolio = () => {
    updatePortfolioMutation.mutate();
  };

  if (walletLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (walletError && !wallet) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <Wallet className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Trading Wallet Found</h2>
          <p className="text-gray-600 mb-6">
            You need to create a trading wallet before you can start trading cryptocurrencies.
          </p>
          <button
            onClick={handleCreateWallet}
            disabled={createWalletMutation.isPending}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <Plus className="h-5 w-5 mr-2" />
            {createWalletMutation.isPending ? 'Creating...' : 'Create Trading Wallet'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Trading Dashboard</h1>
        <button
          onClick={handleUpdatePortfolio}
          disabled={updatePortfolioMutation.isPending}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${updatePortfolioMutation.isPending ? 'animate-spin' : ''}`} />
          Update Prices
        </button>
      </div>

      {/* Wallet Info */}
      {wallet && <WalletInfo wallet={wallet} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trading Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Place Trade</h2>
          <TradingForm
            cryptocurrencies={cryptoList?.items || []}
            selectedSymbol={selectedSymbol}
            onSymbolChange={setSelectedSymbol}
          />
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Stats</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Trades</span>
              <span className="font-semibold">{wallet?.total_trades || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Win Rate</span>
              <span className="font-semibold">{((wallet?.win_rate || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total P&L</span>
              <span className={`font-semibold ${
                (wallet?.total_profit_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${(wallet?.total_profit_loss || 0).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Transaction History */}
      <TransactionHistory />
    </div>
  );
};