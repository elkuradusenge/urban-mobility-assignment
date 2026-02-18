import locationsRouter from "./locationsRouter.js";
import vendorsRouter from "./vendorsRouter.js";
import paymentsRouter from "./paymentsRouter.js";
import tripsRouter from "./tripsRouter.js";
import docsRouter from "./docsRouter.js";

const router = async (req, res) => {
  const url = req.url;
  const method = req.method;

  console.log(`Incoming request: ${method} ${url}`);

  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader(
    "Access-Control-Allow-Methods",
    "GET, POST, PUT, DELETE, OPTIONS",
  );
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // Swagger Documentation
  if (url?.startsWith("/api-docs")) {
    docsRouter(req, res);
    return;
  }

  // Dispatch to sub-routers
  if (url?.startsWith("/locations")) {
    locationsRouter(req, res);
    return;
  }

  if (url?.startsWith("/vendors")) {
    vendorsRouter(req, res);
    return;
  }

  if (url?.startsWith("/payments")) {
    paymentsRouter(req, res);
    return;
  }

  if (url?.startsWith("/trips")) {
    tripsRouter(req, res);
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Route not found" }));
};

export default router;
