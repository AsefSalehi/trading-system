import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const healthCheck = async () => {
  const response = await axios.get('/api/health');
  return response.data;
};

export const HealthCheck: React.FC = () => {
  const { isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    retry: 1,
  });

  if (isLoading) return <div className="text-yellow-600">Checking backend connection...</div>;
  if (isError) return <div className="text-red-600">Backend not available</div>;
  
  return <div className="text-green-600">Backend connected ✓</div>;
};