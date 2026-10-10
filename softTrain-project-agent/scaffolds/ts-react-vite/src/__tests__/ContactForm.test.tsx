import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test } from "vitest";
import { ContactForm } from "../components/ContactForm";

describe("ContactForm", () => {
  test("submit button disabled until form is valid", () => {
    render(<ContactForm />);
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  test("submitting valid input shows confirmation", async () => {
    render(<ContactForm />);
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/name/i), "Ada");
    await user.type(screen.getByLabelText(/email/i), "ada@example.com");
    await user.type(screen.getByLabelText(/message/i), "Hello there.");
    await user.click(screen.getByRole("button", { name: /send/i }));
    expect(screen.getByRole("status")).toHaveTextContent(/ada@example\.com/);
  });

  test("invalid email is flagged", async () => {
    render(<ContactForm />);
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
});
