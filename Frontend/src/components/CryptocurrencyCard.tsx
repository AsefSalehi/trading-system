import React, { useState } from 'react';
import type { Cryptocurrency } from '../types/cryptocurrency';
import { cn, formatCurrency, formatLargeNumber, formatPercentage } from '../lib/utils';
import { TrendingUp, TrendingDown, Star, StarOff, Eye } from 'lucide-react';

interface CryptocurrencyCardProps {
  cryptocurrency: Cryptocurrency;
  className?: string;
  onAddToWatchlist?: (crypto: Cryptocurrency) => void;
  onViewDetails?: (crypto: Cryptocurrency) => void;
  isInWatchlist?: boolean;
}

export const CryptocurrencyCard: React.FC<CryptocurrencyCardProps> = ({
  cryptocurrency,
  className,
  onAddToWatchlist,
  onViewDetails,
  isInWatchlist = false
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  
  const isPositiveChange = cryptocurrency.price_change_percentage_24h >= 0;
  
  // Generate a simple sparkline pattern based on price change
  const generateSparkline = () => {
    const points = [];
    const baseY = 20;
    const amplitude = 10;
    const change = cryptocurrency.price_change_percentage_24h;
    
    for (let i = 0; i <= 20; i++) {
      const x = i * 4;
      const randomVariation = (Math.random() - 0.5) * 4;
      const trendY = baseY - (change / 100) * amplitude * (i / 20);
      const y = trendY + randomVariation;
      points.push(`${x},${Math.max(5, Math.min(35, y))}`);
    }
    return points.join(' ');
  };

  const handleWatchlistToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onAddToWatchlist?.(cryptocurrency);
  };

  const handleViewDetails = () => {
    onViewDetails?.(cryptocurrency);
  };

  return (
    <div 
      className={cn(
        "group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 border border-gray-100 hover:border-blue-200 overflow-hidden cursor-pointer transform hover:scale-[1.02]",
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleViewDetails}
    >
      {/* Gradient overlay on hover */}
      <div className={cn(
        "absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 opacity-0 transition-opacity duration-500",
        isHovered && "opacity-100"
      )} />
      
      {/* Content */}
      <div className="relative p-6">
        {/* Header with crypto info and actions */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="relative">
              {cryptocurrency.image && (
                <>
                  {!isImageLoaded && (
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse" />
                  )}
                  <img
                    src={cryptocurrency.image}
                    alt={cryptocurrency.name}
                    className={cn(
                      "w-12 h-12 rounded-full ring-2 ring-gray-100 transition-all duration-300",
                      isImageLoaded ? "opacity-100" : "opacity-0 absolute inset-0",
                      isHovered && "ring-blue-200 ring-4"
                    )}
                    onLoad={() => setIsImageLoaded(true)}
                  />
                </>
              )}
              {/* Rank badge */}
              <div className="absolute -top-1 -right-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                {cryptocurrency.market_cap_rank}
              </div>
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 leading-tight group-hover:text-blue-600 transition-colors duration-300">
                {cryptocurrency.name}
              </h3>
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                {cryptocurrency.symbol}
              </p>
            </div>
          </div>
          
          {/* Action buttons */}
          <div className={cn(
            "flex items-center space-x-2 opacity-0 transition-all duration-300 transform translate-y-2",
            isHovered && "opacity-100 translate-y-0"
          )}>
            <button
              onClick={handleWatchlistToggle}
              className={cn(
                "p-2 rounded-full transition-all duration-200 hover:scale-110",
                isInWatchlist 
                  ? "bg-yellow-100 text-yellow-600 hover:bg-yellow-200" 
                  : "bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
              )}
              title={isInWatchlist ? "Remove from watchlist" : "Add to watchlist"}
            >
              {isInWatchlist ? <Star className="h-4 w-4 fill-current" /> : <StarOff className="h-4 w-4" />}
            </button>
            <button
              className="p-2 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition-all duration-200 hover:scale-110"
              title="View details"
            >
              <Eye className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Price section with trend indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(cryptocurrency.current_price)}
            </p>
            <div className={cn(
              "flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-bold",
              isPositiveChange 
                ? "bg-green-100 text-green-700" 
                : "bg-red-100 text-red-700"
            )}>
              {isPositiveChange ? (
                <TrendingUp className="h-4 w-4" />
              ) : (
                <TrendingDown className="h-4 w-4" />
              )}
              <span>{formatPercentage(cryptocurrency.price_change_percentage_24h)}</span>
            </div>
          </div>
          
          {/* Mini sparkline chart */}
          <div className="h-10 w-full bg-gray-50 rounded-lg p-2 overflow-hidden">
            <svg width="100%" height="100%" viewBox="0 0 80 40" className="w-full h-full">
              <polyline
                fill="none"
                stroke={isPositiveChange ? "#10b981" : "#ef4444"}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={generateSparkline()}
                className="opacity-80"
              />
              <defs>
                <linearGradient id={`gradient-${cryptocurrency.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor={isPositiveChange ? "#10b981" : "#ef4444"} stopOpacity="0.3"/>
                  <stop offset="100%" stopColor={isPositiveChange ? "#10b981" : "#ef4444"} stopOpacity="0"/>
                </linearGradient>
              </defs>
              <polygon
                fill={`url(#gradient-${cryptocurrency.id})`}
                points={`0,40 ${generateSparkline()} 80,40`}
              />
            </svg>
          </div>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors duration-200">
            <p className="text-gray-500 font-medium mb-1">Market Cap</p>
            <p className="font-bold text-gray-900 text-base">
              {formatLargeNumber(cryptocurrency.market_cap)}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors duration-200">
            <p className="text-gray-500 font-medium mb-1">Volume (24h)</p>
            <p className="font-bold text-gray-900 text-base">
              {formatLargeNumber(cryptocurrency.total_volume)}
            </p>
          </div>
        </div>

        {/* Additional info on hover */}
        <div className={cn(
          "mt-4 pt-4 border-t border-gray-100 transition-all duration-300 overflow-hidden",
          isHovered ? "max-h-20 opacity-100" : "max-h-0 opacity-0"
        )}>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Last updated:</span>
            <span className="font-medium text-gray-700">
              {new Date(cryptocurrency.last_updated).toLocaleTimeString()}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-gray-500">Market dominance:</span>
            <span className="font-medium text-gray-700">
              {((cryptocurrency.market_cap / 2500000000000) * 100).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* Animated border on hover */}
      <div className={cn(
        "absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 transition-opacity duration-500",
        isHovered && "opacity-100"
      )} style={{ mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)', maskComposite: 'xor' }} />
    </div>
  );
};
