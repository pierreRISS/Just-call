import { apiUrl } from '../config';

export type Todo = {
  id: number;
  title: string;
  created_at: string;
};

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchTodos(): Promise<Todo[]> {
  const response = await fetch(`${apiUrl}/todos`);
  return parseResponse<Todo[]>(response);
}

export async function createTodo(title: string): Promise<Todo> {
  const response = await fetch(`${apiUrl}/todos`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title }),
  });

  return parseResponse<Todo>(response);
}

export async function deleteTodo(todoId: number): Promise<void> {
  const response = await fetch(`${apiUrl}/todos/${todoId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
}

