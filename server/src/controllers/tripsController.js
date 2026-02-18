import tripsService from "../services/tripsService.js";
import { bodyParser } from "../utils/bodyParser.js";
import { sendResponse } from "../utils/responseHelper.js";

const getAllTrips = (req, res) => {
  try {
    const trips = tripsService.getAllTrips();
    sendResponse(res, 200, true, trips);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getTripById = (req, res, id) => {
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

const createTrip = async (req, res) => {
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
      const newTrip = tripsService.createTrip(body);
      sendResponse(res, 201, true, newTrip, "Trip created successfully");
    } catch (e) {
      sendResponse(res, 400, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updateTrip = async (req, res, id) => {
  try {
    const body = await bodyParser(req);
    try {
      const updatedTrip = tripsService.updateTrip(id, body);

      if (!updatedTrip) {
        sendResponse(res, 404, false, null, "Trip not found");
      } else {
        sendResponse(res, 200, true, updatedTrip, "Trip updated successfully");
      }
    } catch (e) {
      sendResponse(res, 400, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const deleteTrip = (req, res, id) => {
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
