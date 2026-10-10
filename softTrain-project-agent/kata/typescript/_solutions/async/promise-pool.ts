// Reference solution for async/promise-pool.

export async function pool<T>(
    tasks: Array<() => Promise<T>>,
    concurrency: number,
): Promise<T[]> {
    const results = new Array<T>(tasks.length);
    let nextIndex = 0;

    async function worker() {
        while (true) {
            const i = nextIndex++;
            if (i >= tasks.length) return;
            results[i] = await tasks[i]();
        }
    }

    const workers = Array.from({ length: Math.min(concurrency, tasks.length) }, worker);
    await Promise.all(workers);
    return results;
}
