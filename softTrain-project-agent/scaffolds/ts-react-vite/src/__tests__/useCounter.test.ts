import { renderHook, act } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import { useCounter } from "../hooks/useCounter";

describe("useCounter", () => {
  test("default initial value is 0", () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  test("respects custom initial value", () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  test("inc / dec / reset", () => {
    const { result } = renderHook(() => useCounter(5));
    act(() => result.current.inc());
    act(() => result.current.inc());
    expect(result.current.count).toBe(7);
    act(() => result.current.dec());
    expect(result.current.count).toBe(6);
    act(() => result.current.reset());
    expect(result.current.count).toBe(5);
  });
});
