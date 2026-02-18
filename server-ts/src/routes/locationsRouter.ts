import { IncomingMessage, ServerResponse } from "http";
import locationController from "../controllers/locationController";

const locationsRouter = (req: IncomingMessage, res: ServerResponse): void => {
  const { url, method } = req;

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
};

export default locationsRouter;
