# Notes — power-user tricks for React state

(Read this only after you've finished the exercise.)

## The verdict

For *this problem* (a 3-field form), **V1 is best**. Three `useState` calls, no reducer, no object. The simpler answer is the right one.

The point of the tutorial is that **`useReducer` doesn't pay rent** until your state has the following properties:

1. **Multiple fields that change in coordinated ways.** If `setQuantity(0)` should also clear the discount, you start writing `setQuantity(...); setDiscount(false)` everywhere. That's when an action like `{type: "reset"}` becomes worth it.
2. **Many actions that touch many fields.** A toggle on one field doesn't justify a reducer; ten action types acting on five fields does.
3. **You want the action log as documentation.** A reducer enumerates *all the things that can happen* to your state. That's actually useful in complex flows.

## Three smells that say "use a reducer"

- You have `useEffect` chains that update one state when another changes. (You're simulating actions.)
- You're passing 5+ setters to children as props. (You should pass a single `dispatch`.)
- You can't tell the order in which state updates happen. (A reducer linearises them.)

## The bigger trick: derived state

The biggest learning isn't V1 vs V2 vs V3 — it's that **`subtotal` and `total` should NEVER be state**. They're derived from the inputs. If you `useState` them and try to keep them in sync via `useEffect`, you've recreated the dependency tracking React does for free.

```ts
// ❌ Smell: derived data in state
const [subtotal, setSubtotal] = useState(0);
useEffect(() => setSubtotal(quantity * unitPrice), [quantity, unitPrice]);

// ✅ Just compute it.
const subtotal = quantity * unitPrice;
```

If the computation is expensive, *then* reach for `useMemo`. Don't reach for it preventively — re-rendering is cheap.

## When V3 (object useState) is right

Honestly, almost never. It combines the worst of both: you can't update fields independently without `setState(prev => ({...prev, x: y}))` boilerplate, and you don't get the action-log benefits of a reducer.

The exception: when you have **a clear "form state" object** that's saved/loaded as a unit, and the shape is identical to your API payload. Then having it as one object is convenient.

## When to lift state up

- **Two siblings need the same state** → lift to the parent.
- **One ancestor needs to read it** → lift to that ancestor.
- **The whole app needs it** → context or state-management library.

The mistake people make: lifting *too far*. If only `<Form />` and `<FormSummary />` (its direct child) need the state, don't lift it to the page-level component just because you might need it later. Move it back down.

## Further reading

- [React docs — Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure)
- [React docs — Extracting State Logic into a Reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer)
- Kent C. Dodds — *State Colocation will make your React app faster*
