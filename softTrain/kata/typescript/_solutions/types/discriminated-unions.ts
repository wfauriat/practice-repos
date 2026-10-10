// Reference solution for types/discriminated-unions.

export type Shape =
    | { kind: "circle"; radius: number }
    | { kind: "square"; side: number }
    | { kind: "rect"; width: number; height: number };

function unreachable(_x: never): never {
    throw new Error("Unreachable variant");
}

export function area(shape: Shape): number {
    switch (shape.kind) {
        case "circle":
            return Math.PI * shape.radius ** 2;
        case "square":
            return shape.side ** 2;
        case "rect":
            return shape.width * shape.height;
        default:
            return unreachable(shape);
    }
}
