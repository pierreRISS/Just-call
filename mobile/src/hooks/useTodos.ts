import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { createTodo, deleteTodo, fetchTodos } from '../api/todos';

const todosQueryKey = ['todos'];

export function useTodos() {
  return useQuery({
    queryKey: todosQueryKey,
    queryFn: fetchTodos,
  });
}

export function useCreateTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: todosQueryKey });
    },
  });
}

export function useDeleteTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: todosQueryKey });
    },
  });
}

