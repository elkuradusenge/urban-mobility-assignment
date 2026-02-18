import { IncomingMessage, ServerResponse } from "http";
import tripsController from "../controllers/tripsController";

const tripsRouter = (req: IncomingMessage, res: ServerResponse): void => {
  const { url, method } = req;

  if (url === "/trips") {
    if (method === "GET") {
      tripsController.getAllTrips(req, res);
      return;
    }
    if (method === "POST") {
      tripsController.createTrip(req, res);
      return;
    }
  }

  if (url?.startsWith("/trips/")) {
    const urlParts = url.split("/");
    if (urlParts.length === 3 && urlParts[1] === "trips") {
      const id = parseInt(urlParts[2]);
      if (!isNaN(id)) {
        if (method === "GET") {
          tripsController.getTripById(req, res, id);
          return;
        }
        if (method === "PUT") {
          tripsController.updateTrip(req, res, id);
          return;
        }
        if (method === "DELETE") {
          tripsController.deleteTrip(req, res, id);
          return;
        }
      }
    }
  }
};

export default tripsRouter;
