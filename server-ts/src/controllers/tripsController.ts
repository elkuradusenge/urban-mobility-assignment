import { IncomingMessage, ServerResponse } from "http";
import tripsService from "../services/tripsService";
import { Trip } from "../types";
import { bodyParser } from "../utils/bodyParser";
import { sendResponse } from "../utils/responseHelper";

const getAllTrips = (req: IncomingMessage, res: ServerResponse): void => {
  try {
    const trips = tripsService.getAllTrips();
    sendResponse(res, 200, true, trips);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getTripById = (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): void => {
  try {
    const trip = tripsService.getTripById(id);
    if (!trip) {
      sendResponse(res, 404, false, null, "Trip not found");
    } else {
      sendResponse(res, 200, true, trip);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const createTrip = async (
  req: IncomingMessage,
  res: ServerResponse,
): Promise<void> => {
  try {
    const body = await bodyParser(req);
    // Basic validation for required fields
    const requiredFields = [
      "vendor_id",
      "pickup_datetime",
      "dropoff_datetime",
      "passenger_count",
      "trip_distance",
      "pickup_location_id",
      "dropoff_location_id",
      "fare_amount",
      "total_amount",
    ];
    const missingFields = requiredFields.filter((field) => !body[field]);

    if (missingFields.length > 0) {
      sendResponse(
        res,
        400,
        false,
        null,
        `Missing required fields: ${missingFields.join(", ")}`,
      );
      return;
    }

    try {
      const newTrip = tripsService.createTrip(body as Trip);
      sendResponse(res, 201, true, newTrip, "Trip created successfully");
    } catch (e: any) {
      // Catch bad foreign keys or other validation errors as 400 Bad Request
      // or 409 if it was a conflict (though checking FKs usually implies 400 or 404,
      // but here we validate them before insertion).
      // The Service throws errors like "Vendor ... not found".
      // We'll treat these logic errors as 400 for now, or 404?
      // Usually "Reference not found" is a 400 Bad Request (Invalid input).
      sendResponse(res, 400, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updateTrip = async (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): Promise<void> => {
  try {
    const body = await bodyParser(req);
    try {
      const updatedTrip = tripsService.updateTrip(id, body);

      if (!updatedTrip) {
        sendResponse(res, 404, false, null, "Trip not found");
      } else {
        sendResponse(res, 200, true, updatedTrip, "Trip updated successfully");
      }
    } catch (e: any) {
      sendResponse(res, 400, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const deleteTrip = (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): void => {
  try {
    const success = tripsService.deleteTrip(id);
    if (!success) {
      sendResponse(res, 404, false, null, "Trip not found");
    } else {
      sendResponse(res, 200, true, null, "Trip deleted successfully");
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

export default {
  getAllTrips,
  getTripById,
  createTrip,
  updateTrip,
  deleteTrip,
};
