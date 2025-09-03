import React from 'react';
import type { Cryptocurrency } from '../types/cryptocurrency';
import { cn, formatCurrency, formatLargeNumber, formatPercentage, getValueColor } from '../lib/utils';

interface CryptocurrencyCardProps {
  cryptocurrency: Cryptocurrency;
  className?: string;
}

export const CryptocurrencyCard: React.FC<CryptocurrencyCardProps> = ({
  cryptocurrency,
  className
}) => {
  const priceChangeColor = getValueColor(cryptocurrency.price_change_percentage_24h);

  return (
    <div className={cn(
      "bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-blue-200",
      className
    )}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {cryptocurrency.image && (
            <img
              src={cryptocurrency.image}
              alt={cryptocurrency.name}
              className="w-10 h-10 rounded-full ring-2 ring-gray-100"
            />
          )}
          <div>
            <h3 className="text-lg font-bold text-gray-900 leading-tight">
              {cryptocurrency.name}
            </h3>
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              {cryptocurrency.symbol}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-gray-900">
            {formatCurrency(cryptocurrency.current_price)}
          </p>
          <p className={cn("text-sm font-bold", priceChangeColor)}>
            {formatPercentage(cryptocurrency.price_change_percentage_24h)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 text-sm mt-6 pt-4 border-t border-gray-100">
        <div className="space-y-1">
          <p className="text-gray-500 font-medium">Market Cap</p>
          <p className="font-bold text-gray-900 text-base">
            {formatLargeNumber(cryptocurrency.market_cap)}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-gray-500 font-medium">Rank</p>
          <p className="font-bold text-gray-900 text-base">
            #{cryptocurrency.market_cap_rank}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-gray-500 font-medium">Volume (24h)</p>
          <p className="font-bold text-gray-900 text-base">
            {formatLargeNumber(cryptocurrency.total_volume)}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-gray-500 font-medium">Last Updated</p>
          <p className="font-bold text-gray-900 text-base">
            {new Date(cryptocurrency.last_updated).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
};
