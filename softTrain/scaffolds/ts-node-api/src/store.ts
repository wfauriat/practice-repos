// In-memory item store. Per-app instance, so each test gets a fresh one when re-imported.

export interface Item {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export class Store {
  private items = new Map<number, Item>();
  private nextId = 1;

  list(limit: number, offset: number): { items: Item[]; total: number } {
    const all = [...this.items.values()].sort((a, b) => a.id - b.id);
    return { items: all.slice(offset, offset + limit), total: all.length };
  }

  get(id: number): Item | undefined {
    return this.items.get(id);
  }

  create(name: string, description?: string): Item {
    const now = new Date().toISOString();
    const item: Item = {
      id: this.nextId++,
      name,
      description: description ?? null,
      created_at: now,
      updated_at: now,
    };
    this.items.set(item.id, item);
    return item;
  }

  update(id: number, patch: { name?: string; description?: string }): Item | undefined {
    const existing = this.items.get(id);
    if (!existing) return undefined;
    const updated: Item = {
      ...existing,
      ...patch,
      description: patch.description ?? existing.description,
      updated_at: new Date().toISOString(),
    };
    this.items.set(id, updated);
    return updated;
  }

  delete(id: number): boolean {
    return this.items.delete(id);
  }

  clear() {
    this.items.clear();
    this.nextId = 1;
  }
}

export const store = new Store();
