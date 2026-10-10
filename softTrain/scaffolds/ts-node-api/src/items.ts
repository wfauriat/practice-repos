import { Hono } from "hono";
import { ItemCreate, ItemUpdate, ListQuery } from "./schemas.js";
import { store } from "./store.js";

export const items = new Hono();

items.get("/", (c) => {
  const parsed = ListQuery.safeParse(Object.fromEntries(new URL(c.req.url).searchParams));
  if (!parsed.success) return c.json({ error: parsed.error.flatten() }, 422);
  const { limit, offset } = parsed.data;
  const result = store.list(limit, offset);
  return c.json({ ...result, limit, offset });
});

items.post("/", async (c) => {
  const body = await c.req.json().catch(() => null);
  const parsed = ItemCreate.safeParse(body);
  if (!parsed.success) return c.json({ error: parsed.error.flatten() }, 422);
  const item = store.create(parsed.data.name, parsed.data.description);
  return c.json(item, 201);
});

items.get("/:id", (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid id" }, 422);
  const item = store.get(id);
  return item ? c.json(item) : c.json({ error: "item not found" }, 404);
});

items.patch("/:id", async (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid id" }, 422);
  const body = await c.req.json().catch(() => null);
  const parsed = ItemUpdate.safeParse(body);
  if (!parsed.success) return c.json({ error: parsed.error.flatten() }, 422);
  const updated = store.update(id, parsed.data);
  return updated ? c.json(updated) : c.json({ error: "item not found" }, 404);
});

items.delete("/:id", (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) return c.json({ error: "invalid id" }, 422);
  return store.delete(id) ? c.body(null, 204) : c.json({ error: "item not found" }, 404);
});
