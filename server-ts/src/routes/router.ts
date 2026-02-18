import { IncomingMessage, ServerResponse } from "http";
import locationController from "../controllers/locationController";
import tripsController from "../controllers/tripsController";
import vendorsController from "../controllers/vendorsController";
import paymentsController from "../controllers/paymentsController";

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

  // Locations Routes
  if (url === "/locations") {
    if (method === "GET") {
      locationController.getAllLocations(req, res);
      return;
    }

    if (method === "POST") {
      locationController.createLocation(req, res);
      return;
    }
  }

  if (url?.startsWith("/locations/")) {
    const urlParts = url.split("/");
    if (urlParts.length === 3 && urlParts[1] === "locations") {
      const id = parseInt(urlParts[2]);
      if (!isNaN(id)) {
        if (method === "GET") {
          locationController.getLocationById(req, res, id);
          return;
        }
        if (method === "PUT") {
          locationController.updateLocation(req, res, id);
          return;
        }
        if (method === "DELETE") {
          locationController.deleteLocation(req, res, id);
          return;
        }
      }
    }
  }

  // Other Routes
  if (method === "GET") {
    if (url === "/trips") {
      tripsController.getAllTrips(req, res);
      return;
    }
    if (url === "/vendors") {
      vendorsController.getAllVendors(req, res);
      return;
    }
    if (url === "/payments") {
      paymentsController.getAllPayments(req, res);
      return;
    }
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Route not found" }));
};

export default router;
