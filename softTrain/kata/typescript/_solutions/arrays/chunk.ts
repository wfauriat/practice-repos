// Reference solution for arrays/chunk.

export function chunk<T>(arr: T[], n: number): T[][] {
    if (!Number.isInteger(n) || n <= 0) {
        throw new TypeError(`chunk size must be a positive integer, got ${n}`);
    }
    const out: T[][] = [];
    for (let i = 0; i < arr.length; i += n) {
        out.push(arr.slice(i, i + n));
    }
    return out;
}
