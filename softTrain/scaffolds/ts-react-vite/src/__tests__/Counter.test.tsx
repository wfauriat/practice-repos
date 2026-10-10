import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test } from "vitest";
import { Counter } from "../components/Counter";

describe("Counter", () => {
  test("starts at 0", () => {
    render(<Counter />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  test("increments and decrements", async () => {
    render(<Counter />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "+" }));
    await user.click(screen.getByRole("button", { name: "+" }));
    expect(screen.getByText("2")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "−" }));
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  test("reset returns to initial value", async () => {
    render(<Counter />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "+" }));
    await user.click(screen.getByRole("button", { name: "reset" }));
    expect(screen.getByText("0")).toBeInTheDocument();
  });
});
