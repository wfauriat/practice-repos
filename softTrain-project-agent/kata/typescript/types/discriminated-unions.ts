/**
 * Given the discriminated union below, write `area(shape)` so that:
 *   - it computes the area for each shape
 *   - the `switch` is *exhaustive*: if a new variant is added without a case,
 *     TypeScript should error at compile time.
 *
 * Power-user note: the canonical way to enforce exhaustiveness is to handle
 * the `never` type in the default case. Don't just throw at runtime — use the
 * compiler to catch it.
 */

export type Shape =
    | { kind: "circle"; radius: number }
    | { kind: "square"; side: number }
    | { kind: "rect"; width: number; height: number };

export function area(shape: Shape): number {
    throw new Error("Not implemented");
}

if (import.meta.vitest) {
    const { test, expect, describe } = import.meta.vitest;

    describe("area", () => {
        test("circle", () => {
            expect(area({ kind: "circle", radius: 1 })).toBeCloseTo(Math.PI);
        });
        test("square", () => {
            expect(area({ kind: "square", side: 3 })).toBe(9);
        });
        test("rect", () => {
            expect(area({ kind: "rect", width: 2, height: 5 })).toBe(10);
        });
    });
}
