import locationService from "../services/locationService.js";
import { bodyParser } from "../utils/bodyParser.js";
import { sendResponse } from "../utils/responseHelper.js";

const getAllLocations = (req, res) => {
  try {
    const locations = locationService.getAllLocations();
    sendResponse(res, 200, true, locations);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getLocationById = (req, res, id) => {
  try {
    const location = locationService.getLocationById(id);
    if (!location) {
      sendResponse(res, 404, false, null, "Location not found");
    } else {
      sendResponse(res, 200, true, location);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const createLocation = async (req, res) => {
  try {
    const body = await bodyParser(req);
    const missingFields = [];
    if (!body.borough) missingFields.push("borough");
    if (!body.zone) missingFields.push("zone");
    if (!body.service_zone) missingFields.push("service_zone");

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
      const newLocation = locationService.createLocation(body);
      sendResponse(
        res,
        201,
        true,
        newLocation,
        "Location created successfully",
      );
    } catch (e) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updateLocation = async (req, res, id) => {
  try {
    const body = await bodyParser(req);
    const updatedLocation = locationService.updateLocation(id, body);

    if (!updatedLocation) {
      sendResponse(res, 404, false, null, "Location not found");
    } else {
      sendResponse(
        res,
        200,
        true,
        updatedLocation,
        "Location updated successfully",
      );
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const deleteLocation = (req, res, id) => {
  try {
    const success = locationService.deleteLocation(id);
    if (!success) {
      sendResponse(res, 404, false, null, "Location not found");
    } else {
      sendResponse(res, 200, true, null, "Location deleted successfully");
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

export default {
  getAllLocations,
  getLocationById,
  createLocation,
  updateLocation,
  deleteLocation,
};
