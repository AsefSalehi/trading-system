import React from 'react';
import { TrendingUp } from 'lucide-react';

interface GlobalLoaderProps {
  message?: string;
  submessage?: string;
}

export const GlobalLoader: React.FC<GlobalLoaderProps> = ({ 
  message = "Loading Trading System",
  submessage = "Preparing your trading environment..."
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white rounded-2xl shadow-2xl p-12 text-center max-w-md">
        {/* Animated logo */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-4 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
            <TrendingUp className="h-10 w-10 text-white" />
          </div>
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto"></div>
        </div>
        
        <h3 className="text-xl font-bold text-gray-900 mb-2">{message}</h3>
        <p className="text-gray-600">{submessage}</p>
        
        {/* Progress dots */}
        <div className="flex justify-center space-x-2 mt-6">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
        </div>
      </div>
    </div>
  );
};