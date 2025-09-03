import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Development helper functions for easier testing
if (import.meta.env.DEV) {
  // Add global helper functions for debugging
  (window as any).forceLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.reload();
  };
  
  (window as any).debugAuth = () => {
    console.log('Auth Token:', localStorage.getItem('auth_token'));
    console.log('User Data:', localStorage.getItem('user_data'));
  };
  
  console.log('%c🚀 Trading System Development Mode', 'color: #10b981; font-size: 14px; font-weight: bold;');
  console.log('%c💡 Helper functions available:', 'color: #3b82f6; font-weight: bold;');
  console.log('%c   window.forceLogout() - Clear auth and reload', 'color: #6b7280;');
  console.log('%c   window.debugAuth() - Show auth state', 'color: #6b7280;');
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
