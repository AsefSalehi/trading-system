import React, { useState } from 'react';
import { Navigation } from './Navigation';
import { CryptocurrencyDashboard } from '../CryptocurrencyDashboard';
import { TradingDashboard } from '../Trading/TradingDashboard';
import { PortfolioDashboard } from '../Portfolio/PortfolioDashboard';
import { RiskDashboard } from '../Risk/RiskDashboard';
import { HealthCheck } from '../HealthCheck';

export const MainLayout: React.FC = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
    <div className="flex h-screen bg-gray-50">
      <Navigation
        currentView={currentView}
        onViewChange={setCurrentView}
        isMobileMenuOpen={isMobileMenuOpen}
        setIsMobileMenuOpen={setIsMobileMenuOpen}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-0">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="lg:ml-0 ml-16">
              <h2 className="text-2xl font-bold text-gray-900 capitalize">
                {currentView === 'dashboard' ? 'Market Overview' : currentView}
              </h2>
            </div>
            <HealthCheck />
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  );
};