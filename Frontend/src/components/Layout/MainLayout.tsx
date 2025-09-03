import React, { useState } from 'react';
import { Navigation } from './Navigation';
import { CryptocurrencyDashboard } from '../CryptocurrencyDashboard';
import { TradingDashboard } from '../Trading/TradingDashboard';
import { PortfolioDashboard } from '../Portfolio/PortfolioDashboard';
import { RiskDashboard } from '../Risk/RiskDashboard';
import { HealthCheck } from '../HealthCheck';
import { useAuth } from '../../contexts/AuthContext';

export const MainLayout: React.FC = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { forceLogout } = useAuth();

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <CryptocurrencyDashboard />;
      case 'trading':
        return <TradingDashboard />;
      case 'portfolio':
        return <PortfolioDashboard />;
      case 'risk':
        return <RiskDashboard />;
      default:
        return <CryptocurrencyDashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation
        currentView={currentView}
        onViewChange={setCurrentView}
        isMobileMenuOpen={isMobileMenuOpen}
        setIsMobileMenuOpen={setIsMobileMenuOpen}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-0">
        {/* Header */}
        <header className="bg-white shadow-lg border-b border-gray-200 px-6 py-4 backdrop-blur-sm bg-white/95">
          <div className="flex items-center justify-between">
            <div className="lg:ml-0 ml-16">
              <h2 className="text-2xl font-bold text-gray-900 capitalize">
                {currentView === 'dashboard' ? 'Market Overview' : currentView}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {currentView === 'dashboard' && 'Real-time cryptocurrency market data'}
                {currentView === 'trading' && 'Execute trades and manage orders'}
                {currentView === 'portfolio' && 'Track your investments and performance'}
                {currentView === 'risk' && 'Monitor and assess investment risks'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {/* Development helper button */}
              <button
                onClick={forceLogout}
                className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                title="Development: Test login forms"
              >
                Test Login
              </button>
              <HealthCheck />
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  );
};