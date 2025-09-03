import React from 'react';
import { TrendingUp, Wallet, BarChart3, Shield, ArrowRight } from 'lucide-react';
import { SystemStatus } from './SystemStatus';

interface WelcomeCardProps {
  onNavigate: (view: string) => void;
}

export const WelcomeCard: React.FC<WelcomeCardProps> = ({ onNavigate }) => {
  const features = [
    {
      id: 'trading',
      title: 'Start Trading',
      description: 'Buy and sell cryptocurrencies with real-time market data',
      icon: Wallet,
      bgColor: 'bg-blue-100',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200',
      hoverColor: 'hover:bg-blue-50',
    },
    {
      id: 'portfolio',
      title: 'Track Portfolio',
      description: 'Monitor your holdings and performance metrics',
      icon: BarChart3,
      bgColor: 'bg-green-100',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200',
      hoverColor: 'hover:bg-green-50',
    },
    {
      id: 'risk',
      title: 'Risk Analysis',
      description: 'Assess and manage your trading risks',
      icon: Shield,
      bgColor: 'bg-orange-100',
      iconColor: 'text-orange-600',
      borderColor: 'border-orange-200',
      hoverColor: 'hover:bg-orange-50',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-6">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-full p-4">
            <TrendingUp className="h-16 w-16 text-white" />
          </div>
        </div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
          Welcome to Trading System
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          A comprehensive cryptocurrency trading platform designed for learning and practice. 
          Explore real-time market data, execute trades, and manage your portfolio with advanced risk assessment tools.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <div
              key={feature.id}
              className={`bg-white rounded-2xl shadow-lg p-8 hover:shadow-2xl transition-all duration-300 cursor-pointer border-2 ${feature.borderColor} ${feature.hoverColor} group`}
              onClick={() => onNavigate(feature.id)}
            >
              <div className={`h-16 w-16 rounded-2xl ${feature.bgColor} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-200`}>
                <Icon className={`h-8 w-8 ${feature.iconColor}`} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                {feature.description}
              </p>
              <div className="flex items-center text-blue-600 hover:text-blue-700 font-medium">
                <span>Get started</span>
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform duration-200" />
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl p-8 border-2 border-blue-200 shadow-lg">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Key Features
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-4">
                <div className="h-3 w-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mt-2"></div>
                <div>
                  <h4 className="font-bold text-gray-900 text-lg">Real-time Market Data</h4>
                  <p className="text-gray-600 mt-1">Live cryptocurrency prices and market information</p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="h-3 w-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mt-2"></div>
                <div>
                  <h4 className="font-bold text-gray-900 text-lg">Portfolio Management</h4>
                  <p className="text-gray-600 mt-1">Track holdings, P&L, and performance metrics</p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="h-3 w-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mt-2"></div>
                <div>
                  <h4 className="font-bold text-gray-900 text-lg">Risk Assessment</h4>
                  <p className="text-gray-600 mt-1">Advanced risk analysis and alerts</p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="h-3 w-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mt-2"></div>
                <div>
                  <h4 className="font-bold text-gray-900 text-lg">Educational Focus</h4>
                  <p className="text-gray-600 mt-1">Designed for learning and practice</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div>
          <SystemStatus />
        </div>
      </div>
    </div>
  );
};