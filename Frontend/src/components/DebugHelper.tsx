/**
 * @author Qoder AI Assistant
 * @description Debug helper component for testing UI and authentication
 */

import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const DebugHelper: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  if (import.meta.env.PROD) {
    return null; // Don't show in production
  }

  return (
    <div className="fixed top-4 left-4 z-50 bg-black/80 text-white p-4 rounded-lg text-sm font-mono">
      <div className="mb-2 font-bold text-green-400">🐛 Debug Info</div>
      <div>Auth: {isAuthenticated ? '✅ Logged in' : '❌ Not logged in'}</div>
      {user && <div>User: {user.username}</div>}
      <div className="mt-2 space-x-2">
        <button
          onClick={() => (window as any).forceLogout?.()}
          className="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs"
        >
          Force Logout
        </button>
        <button
          onClick={() => (window as any).debugAuth?.()}
          className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs"
        >
          Debug Auth
        </button>
      </div>
    </div>
  );
};