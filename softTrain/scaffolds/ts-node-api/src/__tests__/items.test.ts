import { beforeEach, describe, expect, test } from "vitest";
import { app } from "../server.js";
import { store } from "../store.js";

beforeEach(() => store.clear());

async function postItem(name: string, description?: string) {
  return app.request("/items", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
}

describe("/items", () => {
  test("health", async () => {
    const r = await app.request("/health");
    expect(r.status).toBe(200);
    expect(await r.json()).toEqual({ status: "ok" });
  });

  test("list empty", async () => {
    const r = await app.request("/items");
    expect(r.status).toBe(200);
    expect(await r.json()).toEqual({ items: [], total: 0, limit: 50, offset: 0 });
  });

  test("create then get", async () => {
    const r = await postItem("first", "hello");
    expect(r.status).toBe(201);
    const created = await r.json();
    expect(created.name).toBe("first");

    const r2 = await app.request(`/items/${created.id}`);
    expect(r2.status).toBe(200);
    expect((await r2.json()).description).toBe("hello");
  });

  test("create validation error", async () => {
    const r = await postItem("");
    expect(r.status).toBe(422);
  });

  test("patch partial update", async () => {
    const created = await (await postItem("first")).json();
    const r = await app.request(`/items/${created.id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ description: "added later" }),
    });
    expect(r.status).toBe(200);
    const updated = await r.json();
    expect(updated.description).toBe("added later");
    expect(updated.name).toBe("first");
  });

  test("delete then 404", async () => {
    const created = await (await postItem("doomed")).json();
    const r = await app.request(`/items/${created.id}`, { method: "DELETE" });
    expect(r.status).toBe(204);
    const r2 = await app.request(`/items/${created.id}`);
    expect(r2.status).toBe(404);
  });

  test("pagination", async () => {
    for (let i = 0; i < 5; i++) await postItem(`item-${i}`);
    const r = await app.request("/items?limit=2&offset=0");
    const body = await r.json();
    expect(body.total).toBe(5);
    expect(body.items).toHaveLength(2);
    expect(body.items[0].name).toBe("item-0");

    const r2 = await app.request("/items?limit=2&offset=2");
    const body2 = await r2.json();
    expect(body2.items[0].name).toBe("item-2");
  });

  test("invalid pagination", async () => {
    const r = await app.request("/items?limit=0");
    expect(r.status).toBe(422);
  });
});
