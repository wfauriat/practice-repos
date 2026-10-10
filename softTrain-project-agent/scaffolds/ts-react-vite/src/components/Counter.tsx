import { useCounter } from "../hooks/useCounter";

export function Counter() {
  const { count, inc, dec, reset } = useCounter();
  return (
    <div className="flex items-center gap-3">
      <button onClick={dec} className="px-3 py-1 border rounded">
        −
      </button>
      <span className="w-12 text-center font-mono text-lg">{count}</span>
      <button onClick={inc} className="px-3 py-1 border rounded">
        +
      </button>
      <button onClick={reset} className="ml-3 px-3 py-1 border rounded text-sm text-gray-600">
        reset
      </button>
    </div>
  );
}
