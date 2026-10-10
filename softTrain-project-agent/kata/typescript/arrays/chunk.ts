/**
 * Split an array into chunks of size `n`. The final chunk may be shorter.
 *
 * @example
 *   chunk([1, 2, 3, 4, 5], 2) // -> [[1, 2], [3, 4], [5]]
 *   chunk([], 3)              // -> []
 *
 * Throw a TypeError if `n` is not a positive integer.
 */
export function chunk<T>(arr: T[], n: number): T[][] {
    throw new Error("Not implemented");
}

if (import.meta.vitest) {
    const { test, expect, describe } = import.meta.vitest;

    describe("chunk", () => {
        test("splits evenly", () => {
            expect(chunk([1, 2, 3, 4], 2)).toEqual([[1, 2], [3, 4]]);
        });

        test("trailing partial chunk", () => {
            expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]]);
        });

        test("empty input", () => {
            expect(chunk([], 3)).toEqual([]);
        });

        test("chunk size larger than input", () => {
            expect(chunk([1, 2], 5)).toEqual([[1, 2]]);
        });

        test("invalid size throws", () => {
            expect(() => chunk([1, 2, 3], 0)).toThrow();
            expect(() => chunk([1, 2, 3], -1)).toThrow();
            expect(() => chunk([1, 2, 3], 1.5)).toThrow();
        });
    });
}
