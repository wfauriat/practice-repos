# ts-react-vite

A modern React frontend starter: Vite + TypeScript + Tailwind v4 + TanStack Query + Vitest + Testing Library + ESLint.

## When to reach for this

- You need a SPA with fast dev cycles and modern tooling defaults.
- You want **tests already wired up** (component, hook, integration via Testing Library).
- You want to see TanStack Query and a controlled form pattern done right from the start.

If you need a full-stack pair: combine with `ts-node-api` (Hono).

## Stack

- **Vite** — dev server + build tool
- **React 18** + **TypeScript** (strict)
- **Tailwind v4** via `@tailwindcss/vite`
- **TanStack Query v5** for server state
- **Vitest** + **@testing-library/react** + **jsdom**
- **ESLint** (flat config)

## Layout

```
src/
├── main.tsx                # Entry
├── App.tsx                 # Top-level layout
├── index.css               # @import "tailwindcss"
├── components/
│   ├── Counter.tsx         # Local state via useState
│   ├── TodoList.tsx        # Server state via TanStack Query
│   └── ContactForm.tsx     # Controlled inputs + validation
├── hooks/
│   └── useCounter.ts       # Custom hook (testable in isolation)
├── lib/
│   └── api.ts              # Fake async data layer (swap for real fetch later)
└── __tests__/
    ├── Counter.test.tsx    # Component test
    ├── useCounter.test.ts  # Hook test (renderHook)
    └── ContactForm.test.tsx
```

## Quick start

```bash
pnpm install

pnpm dev          # vite dev server (http://localhost:5173)
pnpm test         # vitest watch mode
pnpm test:run     # one-shot
pnpm build        # type-check + production build
pnpm preview      # serve the build
pnpm lint
```

With `just`:

```bash
just install
just dev
just test
just build
```

## Design notes

- **Local state** (`useState`) for ephemeral UI state. **Server state** (TanStack Query) for anything fetched. Don't conflate them.
- **Custom hooks live in `hooks/`** and are tested with `renderHook` from `@testing-library/react`. If a hook is purely synchronous, you don't need `act()` in modern RTL — but you usually still want it for clarity.
- **Forms are controlled** by default. For complex forms, reach for React Hook Form; for this size, plain state is clearer.
- **Tests sit next to source** in `__tests__/`. Vitest auto-discovers them.
- **`lib/api.ts`** is a fake data layer with `setTimeout`-backed promises. Swap it for `fetch` calls when you have a real backend.
