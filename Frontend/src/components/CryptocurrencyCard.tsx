import React from 'react';
import type { Cryptocurrency } from '../types/cryptocurrency';
import { cn } from '@/lib/utils';

interface CryptocurrencyCardProps {
  cryptocurrency: Cryptocurrency;
  className?: string;
}

export const CryptocurrencyCard: React.FC<CryptocurrencyCardProps> = ({
  cryptocurrency,
  className
}) => {
  const priceChangeColor = cryptocurrency.price_change_percentage_24h >= 0
    ? 'text-green-600'
    : 'text-red-600';

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    }).format(price);
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(2)}M`;
    }
    return `$${marketCap.toLocaleString()}`;
  };

  return (
    <div className={cn(
      "bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200",
      className
    )}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {cryptocurrency.image && (
            <img
              src={cryptocurrency.image}
              alt={cryptocurrency.name}
              className="w-8 h-8 rounded-full"
            />
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {cryptocurrency.name}
            </h3>
            <p className="text-sm text-gray-500 uppercase">
              {cryptocurrency.symbol}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-gray-900">
            {formatPrice(cryptocurrency.current_price)}
          </p>
          <p className={cn("text-sm font-medium", priceChangeColor)}>
            {cryptocurrency.price_change_percentage_24h >= 0 ? '+' : ''}
            {cryptocurrency.price_change_percentage_24h.toFixed(2)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-500">Market Cap</p>
          <p className="font-semibold text-gray-900">
            {formatMarketCap(cryptocurrency.market_cap)}
          </p>
        </div>
        <div>
          <p className="text-gray-500">Rank</p>
          <p className="font-semibold text-gray-900">
            #{cryptocurrency.market_cap_rank}
          </p>
        </div>
        <div>
          <p className="text-gray-500">Volume (24h)</p>
          <p className="font-semibold text-gray-900">
            {formatMarketCap(cryptocurrency.total_volume)}
          </p>
        </div>
        <div>
          <p className="text-gray-500">Last Updated</p>
          <p className="font-semibold text-gray-900">
            {new Date(cryptocurrency.last_updated).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
};
