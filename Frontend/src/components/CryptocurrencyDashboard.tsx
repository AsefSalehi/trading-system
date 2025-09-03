import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cryptocurrencyApi } from '../services/api';
import { CryptocurrencyCard } from './CryptocurrencyCard';
import { WelcomeCard } from './WelcomeCard';
import { Loader2, RefreshCw, Search, Info } from 'lucide-react';

export const CryptocurrencyDashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('market_cap_rank');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');
  const [showWelcome, setShowWelcome] = useState(() => {
    return !localStorage.getItem('hasVisitedDashboard');
  });

  const handleNavigateFromWelcome = (view: string) => {
    localStorage.setItem('hasVisitedDashboard', 'true');
    setShowWelcome(false);
    // This would need to be passed from parent component
    // For now, we'll just hide the welcome card
  };

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
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="bg-white rounded-xl shadow-xl p-8 flex items-center space-x-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="text-xl font-medium text-gray-700">Loading cryptocurrencies...</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="bg-white rounded-xl shadow-xl p-8 text-center max-w-md">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Data</h2>
          <p className="text-gray-600 mb-6 leading-relaxed">
            {error instanceof Error ? error.message : 'Failed to load cryptocurrency data'}
          </p>
          <button
            onClick={handleRefresh}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
      {showWelcome ? (
        <>
          <div className="mb-8">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-6 shadow-lg">
              <div className="flex items-start space-x-3">
                <Info className="h-6 w-6 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-bold text-blue-900 text-lg">Welcome to the Trading System!</h3>
                  <p className="text-blue-700 mt-2 leading-relaxed">
                    This is your market overview dashboard. Explore the features below or browse live cryptocurrency data.
                  </p>
                  <button
                    onClick={() => setShowWelcome(false)}
                    className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-200 font-medium shadow-md hover:shadow-lg"
                  >
                    Continue to market data →
                  </button>
                </div>
              </div>
            </div>
          </div>
          <WelcomeCard onNavigate={handleNavigateFromWelcome} />
          <div className="mt-12 pt-8 border-t border-gray-200">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Live Market Data</h2>
          </div>
        </>
      ) : (
        <div className="mb-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Cryptocurrency Dashboard
              </h1>
              <p className="text-gray-600 mt-2 text-lg">Real-time market data and trading insights</p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isFetching}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 transition-all duration-200 shadow-lg hover:shadow-xl font-medium"
            >
              <RefreshCw className={`h-5 w-5 ${isFetching ? 'animate-spin' : ''}`} />
              <span>Refresh Data</span>
            </button>
          </div>
        </div>
      )}

        {/* Search and Filter Controls */}
        {!showWelcome && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Search & Filter</h3>
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by symbol (e.g., BTC, ETH)"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white"
                />
              </div>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 hover:bg-white transition-all duration-200 font-medium"
              >
                <option value="market_cap_rank">Sort by Rank</option>
                <option value="market_cap">Sort by Market Cap</option>
                <option value="total_volume">Sort by Volume</option>
                <option value="price_change_percentage_24h">Sort by 24h Change</option>
              </select>
              
              <select
                value={order}
                onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')}
                className="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 hover:bg-white transition-all duration-200 font-medium"
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          </div>
        )}

      {/* Cryptocurrency Grid */}
      {cryptocurrencies?.items && cryptocurrencies.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
          {cryptocurrencies.items.map((crypto) => (
            <CryptocurrencyCard
              key={crypto.id}
              cryptocurrency={crypto}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-md mx-auto">
            <p className="text-gray-500 text-xl font-medium mb-2">No cryptocurrencies found</p>
            {searchTerm && (
              <p className="text-gray-400">
                Try adjusting your search term or filters
              </p>
            )}
          </div>
        </div>
      )}

      {/* Pagination Info */}
      {cryptocurrencies && (
        <div className="mt-12 text-center">
          <div className="bg-white rounded-xl shadow-lg p-6 max-w-md mx-auto">
            <p className="text-gray-700 font-medium text-lg">
              Showing <span className="font-bold text-blue-600">{cryptocurrencies.items.length}</span> of{' '}
              <span className="font-bold text-blue-600">{cryptocurrencies.total}</span> cryptocurrencies
            </p>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};