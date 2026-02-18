import { IncomingMessage, ServerResponse } from "http";
import vendorsService from "../services/vendorsService";
import { Vendor } from "../types";
import { bodyParser } from "../utils/bodyParser";
import { sendResponse } from "../utils/responseHelper";

const getAllVendors = (req: IncomingMessage, res: ServerResponse): void => {
  try {
    const vendors = vendorsService.getAllVendors();
    sendResponse(res, 200, true, vendors);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getVendorById = (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): void => {
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

const createVendor = async (
  req: IncomingMessage,
  res: ServerResponse,
): Promise<void> => {
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
      const newVendor = vendorsService.createVendor(body as Vendor);
      sendResponse(res, 201, true, newVendor, "Vendor created successfully");
    } catch (e: any) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updateVendor = async (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): Promise<void> => {
  try {
    const body = await bodyParser(req);
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
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const deleteVendor = (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): void => {
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
