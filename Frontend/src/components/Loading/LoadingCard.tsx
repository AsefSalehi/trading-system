import React from 'react';
import { cn } from '../../lib/utils';

interface LoadingCardProps {
  className?: string;
  showImage?: boolean;
  lines?: number;
}

export const LoadingCard: React.FC<LoadingCardProps> = ({
  className,
  showImage = true,
  lines = 3,
}) => {
  return (
    <div className={cn('bg-white rounded-2xl shadow-lg p-6 animate-pulse', className)}>
      <div className="flex items-center space-x-4 mb-6">
        {showImage && (
          <div className="w-12 h-12 bg-gray-200 rounded-full" />
        )}
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-3 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
      
      <div className="space-y-3">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="flex justify-between">
            <div className="h-3 bg-gray-200 rounded w-1/3" />
            <div className="h-3 bg-gray-200 rounded w-1/4" />
          </div>
        ))}
      </div>
      
      <div className="mt-4 h-10 bg-gray-200 rounded-lg" />
    </div>
  );
};