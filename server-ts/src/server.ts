import http, { IncomingMessage, ServerResponse } from "http";
import { initDb } from "./db/db";
import { seedIfEmpty } from "./db/seed";
import router from "./routes/router";

// Initialize Database
try {
  initDb();
  seedIfEmpty();
} catch (error) {
  console.error("Database initialization failed:", error);
}

const PORT = process.env.PORT || 3000;

const server = http.createServer(
  (req: IncomingMessage, res: ServerResponse) => {
    router(req, res);
  },
);

server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
