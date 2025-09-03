import React, { useState } from 'react';
import type { Holding } from '../../types/trading';
import { TrendingUp, TrendingDown, Package } from 'lucide-react';

interface HoldingsTableProps {
  holdings: Holding[];
}

export const HoldingsTable: React.FC<HoldingsTableProps> = ({ holdings }) => {
  const [sortBy, setSortBy] = useState<keyof Holding>('current_value');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const formatCurrency = (amount: number | undefined) => {
    const safeAmount = amount ?? 0;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(safeAmount);
  };

  const safeNumber = (value: number | undefined): number => {
    return value ?? 0;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleSort = (column: keyof Holding) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const sortedHoldings = [...holdings].sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    }

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortOrder === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    }

    return 0;
  });

  const getSortIcon = (column: keyof Holding) => {
    if (sortBy !== column) return null;
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  if (holdings.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Holdings</h3>
        <p className="text-gray-600">
          You don't have any cryptocurrency holdings yet. Start trading to build your portfolio.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <Package className="h-6 w-6 text-blue-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-900">Current Holdings</h2>
        <span className="ml-2 text-sm text-gray-500">({holdings.length} positions)</span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('symbol')}
              >
                Symbol {getSortIcon('symbol')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('quantity')}
              >
                Quantity {getSortIcon('quantity')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('average_buy_price')}
              >
                Avg. Buy Price {getSortIcon('average_buy_price')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('current_price')}
              >
                Current Price {getSortIcon('current_price')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('total_cost')}
              >
                Total Cost {getSortIcon('total_cost')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('current_value')}
              >
                Current Value {getSortIcon('current_value')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('unrealized_pnl')}
              >
                Unrealized P&L {getSortIcon('unrealized_pnl')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('first_purchase_at')}
              >
                First Purchase {getSortIcon('first_purchase_at')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedHoldings.map((holding) => (
              <tr key={holding.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm font-medium text-gray-900">
                      {holding.symbol}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {safeNumber(holding.quantity).toFixed(6)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCurrency(holding.average_buy_price)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCurrency(holding.current_price)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCurrency(holding.total_cost)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCurrency(holding.current_value)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex items-center">
                    {safeNumber(holding.unrealized_pnl) >= 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                    )}
                    <div className={safeNumber(holding.unrealized_pnl) >= 0 ? 'text-green-600' : 'text-red-600'}>
                      <div className="font-medium">
                        {formatCurrency(holding.unrealized_pnl)}
                      </div>
                      <div className="text-xs">
                        ({safeNumber(holding.unrealized_pnl_percentage).toFixed(2)}%)
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(holding.first_purchase_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Row */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Total Positions:</span>
            <span className="font-semibold">{holdings.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Total Cost:</span>
            <span className="font-semibold">
              {formatCurrency(holdings.reduce((sum, h) => sum + safeNumber(h.total_cost), 0))}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Total Value:</span>
            <span className="font-semibold">
              {formatCurrency(holdings.reduce((sum, h) => sum + safeNumber(h.current_value), 0))}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Total P&L:</span>
            <span className={`font-semibold ${
              holdings.reduce((sum, h) => sum + safeNumber(h.unrealized_pnl), 0) >= 0
                ? 'text-green-600'
                : 'text-red-600'
            }`}>
              {formatCurrency(holdings.reduce((sum, h) => sum + safeNumber(h.unrealized_pnl), 0))}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
