/**
 * Run an array of async tasks with at most `concurrency` running at once.
 * Return results in the same order as the input.
 *
 * @example
 *   await pool([() => Promise.resolve(1), () => Promise.resolve(2)], 1)
 *   // -> [1, 2]
 */
export async function pool<T>(
    tasks: Array<() => Promise<T>>,
    concurrency: number,
): Promise<T[]> {
    throw new Error("Not implemented");
}

if (import.meta.vitest) {
    const { test, expect, describe } = import.meta.vitest;

    function delayed<T>(value: T, ms: number): () => Promise<T> {
        return () => new Promise((r) => setTimeout(() => r(value), ms));
    }

    describe("pool", () => {
        test("preserves input order", async () => {
            const tasks = [delayed(1, 30), delayed(2, 10), delayed(3, 20)];
            expect(await pool(tasks, 2)).toEqual([1, 2, 3]);
        });

        test("respects concurrency", async () => {
            let inFlight = 0;
            let max = 0;
            const make = () => async () => {
                inFlight++;
                max = Math.max(max, inFlight);
                await new Promise((r) => setTimeout(r, 10));
                inFlight--;
                return 1;
            };
            const tasks = Array.from({ length: 8 }, make);
            await pool(tasks, 3);
            expect(max).toBeLessThanOrEqual(3);
        });

        test("empty input", async () => {
            expect(await pool([], 5)).toEqual([]);
        });
    });
}
