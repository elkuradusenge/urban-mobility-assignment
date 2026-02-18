import { IncomingMessage, ServerResponse } from "http";
import vendorsService from "../services/vendorsService";

const getAllVendors = (req: IncomingMessage, res: ServerResponse): void => {
  try {
    const vendors = vendorsService.getAllVendors();
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(vendors));
  } catch (error) {
    console.error(error);
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Internal Server Error" }));
  }
};

export default {
  getAllVendors,
};
