/**
 * Tutorial 01 — React state patterns (exercise).
 *
 * We're going to build the same little form (a "checkout total" calculator)
 * three different ways. The form has:
 *   - quantity (number)
 *   - unit price (number)
 *   - apply 10% discount? (boolean)
 *
 * It displays:
 *   - subtotal = quantity * unitPrice
 *   - total    = subtotal * (discount ? 0.9 : 1)
 *
 * Three implementations, escalating in (apparent) sophistication. Your job
 * is to fill the blanks and then *judge* which one is actually best.
 *
 * Fill in the lines marked `// TUTOR: <hint>`.
 */

import { useReducer, useState } from "react";

// =============================================================================
// V1: Three pieces of useState. The most-junior version.
// =============================================================================

export function CheckoutV1() {
    // TUTOR: declare three pieces of state with useState:
    //   quantity (number, default 1), unitPrice (number, default 0), discount (boolean, default false).
    const [/* ... */] = useState/* ... */;
    const [/* ... */] = useState/* ... */;
    const [/* ... */] = useState/* ... */;

    // TUTOR: compute subtotal and total. These are NOT state — they're derived.
    // (V1's bug is real-world common: people put `subtotal` in state too.)
    const subtotal = 0; // <- replace
    const total = 0;    // <- replace

    return null; // (we don't render — focus on the state shape)
}

// =============================================================================
// V2: useReducer. Discussed: when this becomes the right call.
// =============================================================================

interface CartState {
    quantity: number;
    unitPrice: number;
    discount: boolean;
}

type CartAction =
    | { type: "setQuantity"; value: number }
    | { type: "setUnitPrice"; value: number }
    | { type: "toggleDiscount" }
    | { type: "reset" };

const initial: CartState = { quantity: 1, unitPrice: 0, discount: false };

function reducer(state: CartState, action: CartAction): CartState {
    switch (action.type) {
        // TUTOR: handle each action. For "setQuantity" / "setUnitPrice" return a new state
        // with the value updated. For "toggleDiscount" flip the boolean. For "reset" return
        // `initial`. Don't mutate `state`.
        case "setQuantity":
            return /* ... */;
        case "setUnitPrice":
            return /* ... */;
        case "toggleDiscount":
            return /* ... */;
        case "reset":
            return /* ... */;
    }
}

export function CheckoutV2() {
    const [state, dispatch] = useReducer(reducer, initial);
    const subtotal = state.quantity * state.unitPrice;
    const total = state.discount ? subtotal * 0.9 : subtotal;
    return null;
}

// =============================================================================
// V3: Single useState with an object. A middle ground.
// =============================================================================

export function CheckoutV3() {
    // TUTOR: a single useState<CartState>(initial). All updates go through
    // setState(prev => ({ ...prev, quantity: ... })).
    const [/* ... */] = useState/* ... */;

    return null;
}

// =============================================================================
// The judgement
// =============================================================================
// Once you've completed all three, Claude will ask: WHICH IS BEST FOR THIS PROBLEM?
// Think about it before answering. The answer will surprise some people.
