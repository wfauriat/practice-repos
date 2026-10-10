# Tutorial 01 — React state patterns

## What this is

A guided practice on **when to reach for which state primitive** in React. By the end you'll have built the same small UI three ways (`useState`, `useReducer`, derived state) and understood the trade-offs first-hand.

## What you'll learn

- When `useState` becomes painful and `useReducer` becomes cleaner.
- Why "derived state" is often the right answer (no state at all).
- How to lift state minimally — and the smell of lifting it too far.
- Why "premature `useReducer`" is a real failure mode.

## How to engage

Open `exercise.ts` and tell Claude: *"Tutor me through this."*

Claude will walk you through three implementations of the same UI. Don't peek at `solution.ts` until you're done.

## Prerequisites

Comfortable with React hooks at the `useState` + `useEffect` level.
