import { useState } from "react";

interface FormState {
  name: string;
  email: string;
  message: string;
}

const empty: FormState = { name: "", email: "", message: "" };

function validate(state: FormState) {
  const errors: Partial<Record<keyof FormState, string>> = {};
  if (!state.name.trim()) errors.name = "required";
  if (!/^\S+@\S+\.\S+$/.test(state.email)) errors.email = "invalid email";
  if (state.message.length < 5) errors.message = "too short";
  return errors;
}

export function ContactForm() {
  const [state, setState] = useState<FormState>(empty);
  const [submitted, setSubmitted] = useState<FormState | null>(null);
  const errors = validate(state);
  const valid = Object.keys(errors).length === 0;

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setState((s) => ({ ...s, [key]: value }));
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!valid) return;
    setSubmitted(state);
    setState(empty);
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      <div>
        <label className="block text-sm" htmlFor="name">
          Name
        </label>
        <input
          id="name"
          className="border rounded px-2 py-1 w-full"
          value={state.name}
          onChange={(e) => update("name", e.target.value)}
        />
        {state.name && errors.name && <p className="text-xs text-red-600">{errors.name}</p>}
      </div>
      <div>
        <label className="block text-sm" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          className="border rounded px-2 py-1 w-full"
          value={state.email}
          onChange={(e) => update("email", e.target.value)}
        />
        {state.email && errors.email && <p className="text-xs text-red-600">{errors.email}</p>}
      </div>
      <div>
        <label className="block text-sm" htmlFor="message">
          Message
        </label>
        <textarea
          id="message"
          className="border rounded px-2 py-1 w-full"
          rows={3}
          value={state.message}
          onChange={(e) => update("message", e.target.value)}
        />
        {state.message && errors.message && <p className="text-xs text-red-600">{errors.message}</p>}
      </div>
      <button
        type="submit"
        disabled={!valid}
        className="px-3 py-1 border rounded bg-blue-600 text-white disabled:bg-gray-300"
      >
        Send
      </button>
      {submitted && (
        <p role="status" className="text-sm text-green-700">
          Sent to {submitted.email}
        </p>
      )}
    </form>
  );
}
