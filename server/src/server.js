import http from "http";
import { initDb } from "./db/db.js";
import { seedIfEmpty } from "./db/seed.js";
import router from "./routes/router.js";

// Initialize Database
try {
  initDb();
  seedIfEmpty();
} catch (error) {
  console.error("Database initialization failed:", error);
}

const PORT = process.env.PORT || 3000;

const server = http.createServer(
  (req, res) => {
    router(req, res);
  },
);

server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Swagger docs available at http://localhost:${PORT}/api-docs`);
});
