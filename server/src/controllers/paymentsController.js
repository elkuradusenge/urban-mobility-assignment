import paymentsService from "../services/paymentsService.js";
import { bodyParser } from "../utils/bodyParser.js";
import { sendResponse } from "../utils/responseHelper.js";

const getAllPayments = (req, res) => {
  try {
    const payments = paymentsService.getAllPayments();
    sendResponse(res, 200, true, payments);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getPaymentById = (req, res, id) => {
  try {
    const payment = paymentsService.getPaymentById(id);
    if (!payment) {
      sendResponse(res, 404, false, null, "Payment not found");
    } else {
      sendResponse(res, 200, true, payment);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const createPayment = async (req, res) => {
  try {
    const body = await bodyParser(req);
    const missingFields = [];
    if (!body.name) missingFields.push("name");

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
      const newPayment = paymentsService.createPayment(body);
      sendResponse(res, 201, true, newPayment, "Payment created successfully");
    } catch (e) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updatePayment = async (req, res, id) => {
  try {
    const body = await bodyParser(req);
    try {
      const updatedPayment = paymentsService.updatePayment(id, body);

      if (!updatedPayment) {
        sendResponse(res, 404, false, null, "Payment not found");
      } else {
        sendResponse(
          res,
          200,
          true,
          updatedPayment,
          "Payment updated successfully",
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

const deletePayment = (req, res, id) => {
  try {
    const success = paymentsService.deletePayment(id);
    if (!success) {
      sendResponse(res, 404, false, null, "Payment not found");
    } else {
      sendResponse(res, 200, true, null, "Payment deleted successfully");
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

export default {
  getAllPayments,
  getPaymentById,
  createPayment,
  updatePayment,
  deletePayment,
};
