import { z } from "zod";

export const ItemCreate = z.object({
  name: z.string().min(1).max(200),
  description: z.string().max(2000).optional(),
});

export const ItemUpdate = z.object({
  name: z.string().min(1).max(200).optional(),
  description: z.string().max(2000).optional(),
});

export const ListQuery = z.object({
  limit: z.coerce.number().int().min(1).max(200).default(50),
  offset: z.coerce.number().int().min(0).default(0),
});

export type ItemCreate = z.infer<typeof ItemCreate>;
export type ItemUpdate = z.infer<typeof ItemUpdate>;
export type ListQuery = z.infer<typeof ListQuery>;
