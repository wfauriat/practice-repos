import { useQuery } from "@tanstack/react-query";
import { fetchTodos } from "../lib/api";

export function TodoList() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["todos"],
    queryFn: fetchTodos,
  });

  if (isPending) return <p className="text-gray-500">Loading…</p>;
  if (isError) return <p className="text-red-600">Failed to load.</p>;

  return (
    <ul className="space-y-1">
      {data.map((t) => (
        <li key={t.id} className="flex items-center gap-2">
          <span aria-label={t.done ? "done" : "open"}>{t.done ? "✓" : "·"}</span>
          <span className={t.done ? "line-through text-gray-500" : ""}>{t.title}</span>
        </li>
      ))}
    </ul>
  );
}
