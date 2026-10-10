// Tutorial 01 — React state patterns (reference solution).

import { useReducer, useState } from "react";

// =============================================================================
// V1: Three pieces of useState.
// =============================================================================

export function CheckoutV1() {
    const [quantity, setQuantity] = useState(1);
    const [unitPrice, setUnitPrice] = useState(0);
    const [discount, setDiscount] = useState(false);

    // Derived — not state. This is the key insight.
    const subtotal = quantity * unitPrice;
    const total = discount ? subtotal * 0.9 : subtotal;

    void setQuantity; void setUnitPrice; void setDiscount; // unused-marker for the example
    void subtotal; void total;
    return null;
}

// =============================================================================
// V2: useReducer.
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
        case "setQuantity":
            return { ...state, quantity: action.value };
        case "setUnitPrice":
            return { ...state, unitPrice: action.value };
        case "toggleDiscount":
            return { ...state, discount: !state.discount };
        case "reset":
            return initial;
    }
}

export function CheckoutV2() {
    const [state, dispatch] = useReducer(reducer, initial);
    const subtotal = state.quantity * state.unitPrice;
    const total = state.discount ? subtotal * 0.9 : subtotal;
    void dispatch; void total;
    return null;
}

// =============================================================================
// V3: Single useState with an object.
// =============================================================================

export function CheckoutV3() {
    const [state, setState] = useState<CartState>(initial);
    const subtotal = state.quantity * state.unitPrice;
    const total = state.discount ? subtotal * 0.9 : subtotal;
    void setState; void total;
    return null;
}
