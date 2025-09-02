import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CryptocurrencyDashboard } from './components/CryptocurrencyDashboard';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <CryptocurrencyDashboard />
      </div>
    </QueryClientProvider>
  );
}

export default App;
