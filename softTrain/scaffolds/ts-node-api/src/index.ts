import { serve } from "@hono/node-server";
import { app } from "./server.js";

const port = Number(process.env.PORT ?? 3000);
serve({ fetch: app.fetch, port }, (info) => {
  // eslint-disable-next-line no-console
  console.log(`Listening on http://localhost:${info.port}`);
});
