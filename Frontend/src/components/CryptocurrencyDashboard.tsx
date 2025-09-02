import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cryptocurrencyApi } from '../services/api';
import { CryptocurrencyCard } from './CryptocurrencyCard';
import { Loader2, RefreshCw, Search } from 'lucide-react';

export const CryptocurrencyDashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('market_cap_rank');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');

  const {
    data: cryptocurrencies,
    isLoading,
    isError,
    error,
    refetch,
    isFetching
  } = useQuery({
    queryKey: ['cryptocurrencies', { sortBy, order, searchTerm }],
    queryFn: () => cryptocurrencyApi.getCryptocurrencies({
      limit: 50,
      sort_by: sortBy,
      order,
      symbol_filter: searchTerm || undefined,
    }),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const handleRefresh = () => {
    refetch();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading cryptocurrencies...</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-4">
            {error instanceof Error ? error.message : 'Failed to load cryptocurrency data'}
          </p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Cryptocurrency Dashboard
          </h1>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Search and Filter Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by symbol (e.g., BTC, ETH)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="market_cap_rank">Rank</option>
            <option value="market_cap">Market Cap</option>
            <option value="total_volume">Volume</option>
            <option value="price_change_percentage_24h">24h Change</option>
          </select>
          
          <select
            value={order}
            onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
      </div>

      {/* Cryptocurrency Grid */}
      {cryptocurrencies?.items && cryptocurrencies.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cryptocurrencies.items.map((crypto) => (
            <CryptocurrencyCard
              key={crypto.id}
              cryptocurrency={crypto}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No cryptocurrencies found</p>
          {searchTerm && (
            <p className="text-gray-400 mt-2">
              Try adjusting your search term or filters
            </p>
          )}
        </div>
      )}

      {/* Pagination Info */}
      {cryptocurrencies && (
        <div className="mt-8 text-center text-gray-600">
          <p>
            Showing {cryptocurrencies.items.length} of {cryptocurrencies.total} cryptocurrencies
          </p>
        </div>
      )}
    </div>
  );
};