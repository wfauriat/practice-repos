import { Hono } from "hono";
import { items } from "./items.js";

export const app = new Hono();

app.get("/health", (c) => c.json({ status: "ok" }));
app.route("/items", items);
