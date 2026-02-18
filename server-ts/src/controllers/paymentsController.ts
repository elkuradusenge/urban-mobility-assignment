import { IncomingMessage, ServerResponse } from "http";
import paymentsService from "../services/paymentsService";
import { Payment } from "../types";
import { bodyParser } from "../utils/bodyParser";
import { sendResponse } from "../utils/responseHelper";

const getAllPayments = (req: IncomingMessage, res: ServerResponse): void => {
  try {
    const payments = paymentsService.getAllPayments();
    sendResponse(res, 200, true, payments);
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const getPaymentById = (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): void => {
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

const createPayment = async (
  req: IncomingMessage,
  res: ServerResponse,
): Promise<void> => {
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
      const newPayment = paymentsService.createPayment(body as Payment);
      sendResponse(res, 201, true, newPayment, "Payment created successfully");
    } catch (e: any) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const updatePayment = async (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): Promise<void> => {
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
    } catch (e: any) {
      sendResponse(res, 409, false, null, e.message);
    }
  } catch (error) {
    console.error(error);
    sendResponse(res, 500, false, null, "Internal Server Error");
  }
};

const deletePayment = (
  req: IncomingMessage,
  res: ServerResponse,
  id: number,
): void => {
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
