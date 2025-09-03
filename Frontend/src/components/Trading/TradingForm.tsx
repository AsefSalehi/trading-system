import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tradingApi } from '../../services/tradingApi';
import type { Cryptocurrency } from '../../types/cryptocurrency';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface TradingFormProps {
  cryptocurrencies: Cryptocurrency[];
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

export const TradingForm: React.FC<TradingFormProps> = ({
  cryptocurrencies,
  selectedSymbol,
  onSymbolChange,
}) => {
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const queryClient = useQueryClient();

  const selectedCrypto = cryptocurrencies.find(crypto => crypto.symbol === selectedSymbol);

  const buyMutation = useMutation({
    mutationFn: tradingApi.buyCryptocurrency,
    onSuccess: (data) => {
      setMessage(`✅ ${data.message}`);
      setAmount('');
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
      queryClient.invalidateQueries({ queryKey: ['holdings'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
    onError: (error: any) => {
      setMessage(`❌ ${error.response?.data?.detail || 'Buy order failed'}`);
    },
  });

  const sellMutation = useMutation({
    mutationFn: tradingApi.sellCryptocurrency,
    onSuccess: (data) => {
      setMessage(`✅ ${data.message}`);
      setAmount('');
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
      queryClient.invalidateQueries({ queryKey: ['holdings'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
    onError: (error: any) => {
      setMessage(`❌ ${error.response?.data?.detail || 'Sell order failed'}`);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSymbol || !amount) return;

    setIsLoading(true);
    setMessage('');

    const tradeRequest = {
      symbol: selectedSymbol,
      amount: parseFloat(amount),
    };

    try {
      if (tradeType === 'buy') {
        await buyMutation.mutateAsync(tradeRequest);
      } else {
        await sellMutation.mutateAsync(tradeRequest);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const calculateEstimate = () => {
    if (!selectedCrypto || !amount) return null;
    
    const amountNum = parseFloat(amount);
    if (isNaN(amountNum)) return null;

    if (tradeType === 'buy') {
      // Amount is USD, calculate crypto quantity
      const quantity = amountNum / selectedCrypto.current_price;
      return `≈ ${quantity.toFixed(6)} ${selectedCrypto.symbol}`;
    } else {
      // Amount is crypto quantity, calculate USD value
      const usdValue = amountNum * selectedCrypto.current_price;
      return `≈ $${usdValue.toFixed(2)}`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Trade Type Toggle */}
      <div className="flex rounded-lg bg-gray-100 p-1">
        <button
          type="button"
          onClick={() => setTradeType('buy')}
          className={`flex-1 flex items-center justify-center py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            tradeType === 'buy'
              ? 'bg-green-600 text-white shadow-sm'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          <TrendingUp className="h-4 w-4 mr-2" />
          Buy
        </button>
        <button
          type="button"
          onClick={() => setTradeType('sell')}
          className={`flex-1 flex items-center justify-center py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            tradeType === 'sell'
              ? 'bg-red-600 text-white shadow-sm'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          <TrendingDown className="h-4 w-4 mr-2" />
          Sell
        </button>
      </div>

      {/* Cryptocurrency Selection */}
      <div>
        <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-1">
          Cryptocurrency
        </label>
        <select
          id="symbol"
          value={selectedSymbol}
          onChange={(e) => onSymbolChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        >
          <option value="">Select a cryptocurrency</option>
          {cryptocurrencies.map((crypto) => (
            <option key={crypto.symbol} value={crypto.symbol}>
              {crypto.name} ({crypto.symbol}) - ${crypto.current_price.toFixed(2)}
            </option>
          ))}
        </select>
      </div>

      {/* Amount Input */}
      <div>
        <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-1">
          {tradeType === 'buy' ? 'Amount (USD)' : `Quantity (${selectedSymbol})`}
        </label>
        <input
          id="amount"
          type="number"
          step="0.000001"
          min="0"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder={tradeType === 'buy' ? 'Enter USD amount' : 'Enter quantity'}
          required
        />
        {calculateEstimate() && (
          <p className="mt-1 text-sm text-gray-600">
            {calculateEstimate()}
          </p>
        )}
      </div>

      {/* Current Price Display */}
      {selectedCrypto && (
        <div className="bg-gray-50 rounded-md p-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Current Price:</span>
            <span className="font-semibold">${selectedCrypto.current_price.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center mt-1">
            <span className="text-sm text-gray-600">24h Change:</span>
            <span className={`text-sm font-medium ${
              selectedCrypto.price_change_percentage_24h >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {selectedCrypto.price_change_percentage_24h.toFixed(2)}%
            </span>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !selectedSymbol || !amount}
        className={`w-full py-2 px-4 rounded-md text-white font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
          tradeType === 'buy'
            ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
            : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
        }`}
      >
        {isLoading ? 'Processing...' : `${tradeType === 'buy' ? 'Buy' : 'Sell'} ${selectedSymbol}`}
      </button>

      {/* Message Display */}
      {message && (
        <div className={`p-3 rounded-md text-sm ${
          message.startsWith('✅') 
            ? 'bg-green-50 text-green-700 border border-green-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message}
        </div>
      )}
    </form>
  );
};