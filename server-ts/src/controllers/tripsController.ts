import { IncomingMessage, ServerResponse } from "http";
import tripsService from "../services/tripsService";

const getAllTrips = (req: IncomingMessage, res: ServerResponse): void => {
  try {
    const trips = tripsService.getAllTrips();
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(trips));
  } catch (error) {
    console.error(error);
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Internal Server Error" }));
  }
};

export default {
  getAllTrips,
};
