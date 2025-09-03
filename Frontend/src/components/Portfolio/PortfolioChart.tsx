import React from 'react';
import type { Holding } from '../../types/trading';

interface PortfolioChartProps {
  holdings: Holding[];
}

export const PortfolioChart: React.FC<PortfolioChartProps> = ({ holdings }) => {
  const totalValue = holdings.reduce((sum, holding) => sum + holding.current_value, 0);
  
  // Calculate percentages and prepare data for the chart
  const chartData = holdings
    .map(holding => ({
      symbol: holding.symbol,
      value: holding.current_value,
      percentage: (holding.current_value / totalValue) * 100,
      pnl: holding.unrealized_pnl,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10); // Show top 10 holdings

  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-red-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-gray-500',
    'bg-orange-500',
    'bg-teal-500',
  ];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (holdings.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No holdings to display</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Horizontal Bar Chart */}
      <div className="space-y-3">
        {chartData.map((item, index) => (
          <div key={item.symbol} className="flex items-center space-x-4">
            <div className="w-16 text-sm font-medium text-gray-900">
              {item.symbol}
            </div>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div
                className={`h-6 rounded-full ${colors[index % colors.length]} transition-all duration-300`}
                style={{ width: `${Math.max(item.percentage, 2)}%` }}
              />
              <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                {item.percentage.toFixed(1)}%
              </div>
            </div>
            <div className="w-24 text-sm text-right">
              {formatCurrency(item.value)}
            </div>
            <div className={`w-20 text-sm text-right ${
              item.pnl >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {item.pnl >= 0 ? '+' : ''}{formatCurrency(item.pnl)}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 pt-4 border-t border-gray-200">
        {chartData.map((item, index) => (
          <div key={item.symbol} className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`} />
            <div className="text-sm">
              <div className="font-medium">{item.symbol}</div>
              <div className="text-gray-500">{item.percentage.toFixed(1)}%</div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(totalValue)}
          </div>
          <div className="text-sm text-gray-600">Total Portfolio Value</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {holdings.length}
          </div>
          <div className="text-sm text-gray-600">Total Positions</div>
        </div>
        <div className="text-center">
          <div className={`text-2xl font-bold ${
            chartData.reduce((sum, item) => sum + item.pnl, 0) >= 0 
              ? 'text-green-600' 
              : 'text-red-600'
          }`}>
            {formatCurrency(chartData.reduce((sum, item) => sum + item.pnl, 0))}
          </div>
          <div className="text-sm text-gray-600">Total Unrealized P&L</div>
        </div>
      </div>
    </div>
  );
};