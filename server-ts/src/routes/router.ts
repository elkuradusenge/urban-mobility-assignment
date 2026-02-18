import { IncomingMessage, ServerResponse } from "http";
import locationsRouter from "./locationsRouter";
import vendorsRouter from "./vendorsRouter";
import paymentsRouter from "./paymentsRouter";
import tripsRouter from "./tripsRouter";

const router = async (
  req: IncomingMessage,
  res: ServerResponse,
): Promise<void> => {
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
