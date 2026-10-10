// Fake data layer. Swap for real `fetch()` when you have a backend.

export interface Todo {
  id: number;
  title: string;
  done: boolean;
}

const TODOS: Todo[] = [
  { id: 1, title: "Read the scaffold README", done: true },
  { id: 2, title: "Try editing a component and saving", done: false },
  { id: 3, title: "Replace this fake API with a real one", done: false },
];

export async function fetchTodos(): Promise<Todo[]> {
  await new Promise((r) => setTimeout(r, 200));
  return TODOS.map((t) => ({ ...t }));
}
