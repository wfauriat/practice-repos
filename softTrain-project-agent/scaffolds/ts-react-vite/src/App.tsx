import { Counter } from "./components/Counter";
import { TodoList } from "./components/TodoList";
import { ContactForm } from "./components/ContactForm";

export function App() {
  return (
    <main className="mx-auto max-w-2xl p-8 space-y-12">
      <header>
        <h1 className="text-3xl font-bold">ts-react-vite</h1>
        <p className="text-gray-600">A scaffold demonstrating local state, server state, and forms.</p>
      </header>

      <section>
        <h2 className="text-xl font-semibold mb-2">Local state — Counter</h2>
        <Counter />
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-2">Server state — Todos (TanStack Query)</h2>
        <TodoList />
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-2">Form — Contact</h2>
        <ContactForm />
      </section>
    </main>
  );
}
