import React from 'react';
import type { Wallet } from '../../types/trading';
import { Wallet as WalletIcon, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

interface WalletInfoProps {
  wallet: Wallet;
}

export const WalletInfo: React.FC<WalletInfoProps> = ({ wallet }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (percentage: number) => {
    return `${(percentage * 100).toFixed(1)}%`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <WalletIcon className="h-6 w-6 text-blue-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-900">Trading Wallet</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* USD Balance */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-600">USD Balance</p>
              <p className="text-2xl font-bold text-blue-900">
                {formatCurrency(wallet.usd_balance)}
              </p>
            </div>
          </div>
        </div>

        {/* Total Portfolio Value */}
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-600">Portfolio Value</p>
              <p className="text-2xl font-bold text-green-900">
                {formatCurrency(wallet.total_portfolio_value)}
              </p>
            </div>
          </div>
        </div>

        {/* Total P&L */}
        <div className={`rounded-lg p-4 ${
          wallet.total_profit_loss >= 0 ? 'bg-green-50' : 'bg-red-50'
        }`}>
          <div className="flex items-center">
            {wallet.total_profit_loss >= 0 ? (
              <TrendingUp className="h-8 w-8 text-green-600" />
            ) : (
              <TrendingDown className="h-8 w-8 text-red-600" />
            )}
            <div className="ml-3">
              <p className={`text-sm font-medium ${
                wallet.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                Total P&L
              </p>
              <p className={`text-2xl font-bold ${
                wallet.total_profit_loss >= 0 ? 'text-green-900' : 'text-red-900'
              }`}>
                {wallet.total_profit_loss >= 0 ? '+' : ''}{formatCurrency(wallet.total_profit_loss)}
              </p>
            </div>
          </div>
        </div>

        {/* Win Rate */}
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">%</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-purple-600">Win Rate</p>
              <p className="text-2xl font-bold text-purple-900">
                {formatPercentage(wallet.win_rate)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Total Trades:</span>
            <span className="font-semibold">{wallet.total_trades}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Account Created:</span>
            <span className="font-semibold">
              {new Date(wallet.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};