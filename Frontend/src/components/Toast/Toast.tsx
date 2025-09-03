import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
}

const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const toastStyles = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

const iconStyles = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
};

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  const Icon = toastIcons[type];

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      onClose(id);
    }, 300);
  };

  return (
    <div
      className={cn(
        'transform transition-all duration-300 ease-in-out mb-4',
        isVisible && !isExiting
          ? 'translate-x-0 opacity-100 scale-100'
          : 'translate-x-full opacity-0 scale-95'
      )}
    >
      <div
        className={cn(
          'max-w-sm w-full shadow-lg rounded-xl border backdrop-blur-sm',
          toastStyles[type]
        )}
      >
        <div className="p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <Icon className={cn('h-6 w-6', iconStyles[type])} />
            </div>
            <div className="ml-3 w-0 flex-1">
              <p className="text-sm font-semibold">{title}</p>
              {message && (
                <p className="mt-1 text-sm opacity-90">{message}</p>
              )}
            </div>
            <div className="ml-4 flex-shrink-0 flex">
              <button
                onClick={handleClose}
                className={cn(
                  'inline-flex rounded-md p-1.5 transition-colors duration-200',
                  type === 'success' && 'text-green-500 hover:bg-green-100',
                  type === 'error' && 'text-red-500 hover:bg-red-100',
                  type === 'warning' && 'text-yellow-500 hover:bg-yellow-100',
                  type === 'info' && 'text-blue-500 hover:bg-blue-100'
                )}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
        {/* Progress bar */}
        {duration > 0 && (
          <div className="h-1 bg-black/10 rounded-b-xl overflow-hidden">
            <div
              className={cn(
                'h-full transition-all ease-linear',
                type === 'success' && 'bg-green-500',
                type === 'error' && 'bg-red-500',
                type === 'warning' && 'bg-yellow-500',
                type === 'info' && 'bg-blue-500'
              )}
              style={{
                animation: `shrink ${duration}ms linear`,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

// Add the shrink animation to CSS
const style = document.createElement('style');
style.textContent = `
  @keyframes shrink {
    from { width: 100%; }
    to { width: 0%; }
  }
`;
document.head.appendChild(style);