import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const healthCheck = async () => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  const healthURL = baseURL.replace('/api/v1', '/health');
  const response = await axios.get(healthURL);
  return response.data;
};

export const HealthCheck: React.FC = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    retry: 1,
    refetchInterval: 30000, // Check every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2 text-yellow-600">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
        <span className="text-sm">Checking backend...</span>
      </div>
    );
  }
  
  if (isError) {
    return (
      <div className="flex items-center space-x-2 text-red-600">
        <div className="h-2 w-2 bg-red-600 rounded-full"></div>
        <span className="text-sm">Backend offline</span>
      </div>
    );
  }
  
  return (
    <div className="flex items-center space-x-2 text-green-600">
      <div className="h-2 w-2 bg-green-600 rounded-full animate-pulse"></div>
      <span className="text-sm">Backend connected</span>
      {data?.version && (
        <span className="text-xs text-gray-500">v{data.version}</span>
      )}
    </div>
  );
};