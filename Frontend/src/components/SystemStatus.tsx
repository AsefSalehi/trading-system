import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { tradingApi } from '../services/tradingApi';
import { cryptocurrencyApi } from '../services/api';
import { CheckCircle, AlertCircle, TrendingUp, Wallet, Database } from 'lucide-react';

export const SystemStatus: React.FC = () => {
  // Check wallet status
  const { data: wallet, isLoading: walletLoading, error: walletError } = useQuery({
    queryKey: ['wallet'],
    queryFn: tradingApi.getWallet,
    retry: false,
  });

  // Check market data availability
  const { data: cryptoData, isLoading: cryptoLoading, error: cryptoError } = useQuery({
    queryKey: ['crypto-status'],
    queryFn: () => cryptocurrencyApi.getCryptocurrencies({ limit: 1 }),
    retry: false,
  });

  const statusItems = [
    {
      name: 'Market Data',
      status: cryptoLoading ? 'loading' : cryptoError ? 'error' : 'success',
      message: cryptoLoading 
        ? 'Loading...' 
        : cryptoError 
          ? 'Market data unavailable' 
          : `${cryptoData?.total || 0} cryptocurrencies available`,
      icon: Database,
    },
    {
      name: 'Trading Wallet',
      status: walletLoading ? 'loading' : walletError ? 'warning' : 'success',
      message: walletLoading 
        ? 'Loading...' 
        : walletError 
          ? 'No wallet created yet' 
          : `Balance: $${wallet?.usd_balance?.toFixed(2) || '0.00'}`,
      icon: Wallet,
    },
    {
      name: 'System Health',
      status: 'success',
      message: 'All systems operational',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
      <div className="space-y-3">
        {statusItems.map((item) => {
          const Icon = item.icon;
          const getStatusColor = () => {
            switch (item.status) {
              case 'success': return 'text-green-600';
              case 'warning': return 'text-yellow-600';
              case 'error': return 'text-red-600';
              default: return 'text-gray-600';
            }
          };

          const getStatusIcon = () => {
            switch (item.status) {
              case 'success': return <CheckCircle className="h-5 w-5 text-green-600" />;
              case 'warning': 
              case 'error': return <AlertCircle className={`h-5 w-5 ${getStatusColor()}`} />;
              default: return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>;
            }
          };

          return (
            <div key={item.name} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Icon className={`h-5 w-5 ${getStatusColor()}`} />
                <span className="font-medium text-gray-900">{item.name}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-sm ${getStatusColor()}`}>{item.message}</span>
                {getStatusIcon()}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};