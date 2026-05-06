import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { TodosScreen } from './src/screens/TodosScreen';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TodosScreen />
    </QueryClientProvider>
  );
}
