import vendorsService from "../services/vendorsService.js";
import { bodyParser } from "../utils/bodyParser.js";
import { sendResponse } from "../utils/responseHelper.js";

const getAllVendors = (req, res) => {
  try {
    const vendors = vendorsService.getAllVendors();
    sendResponse(res, 200, true, vendors);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getVendorById = (req, res, id) => {
  try {
    const vendor = vendorsService.getVendorById(id);
    if (!vendor) {
      sendResponse(res, 404, false, null, "Vendor not found");
    } else {
      sendResponse(res, 200, true, vendor);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const createVendor = async (req, res) => {
  try {
    const body = await bodyParser(req);
    const missingFields = [];
    if (!body.name) missingFields.push("name");
    if (!body.email) missingFields.push("email");
    if (!body.phone_number) missingFields.push("phone_number");

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
      const newVendor = vendorsService.createVendor(body);
      sendResponse(res, 201, true, newVendor, "Vendor created successfully");
    } catch (e) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updateVendor = async (req, res, id) => {
  try {
    const body = await bodyParser(req);
    try {
      const updatedVendor = vendorsService.updateVendor(id, body);

      if (!updatedVendor) {
        sendResponse(res, 404, false, null, "Vendor not found");
      } else {
        sendResponse(
          res,
          200,
          true,
          updatedVendor,
          "Vendor updated successfully",
        );
      }
    } catch (e) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const deleteVendor = (req, res, id) => {
  try {
    const success = vendorsService.deleteVendor(id);
    if (!success) {
      sendResponse(res, 404, false, null, "Vendor not found");
    } else {
      sendResponse(res, 200, true, null, "Vendor deleted successfully");
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

export default {
  getAllVendors,
  getVendorById,
  createVendor,
  updateVendor,
  deleteVendor,
};
