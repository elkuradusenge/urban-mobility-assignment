import { IncomingMessage, ServerResponse } from "http";
import paymentsService from "../services/paymentsService";

const getAllPayments = (req: IncomingMessage, res: ServerResponse): void => {
  try {
    const payments = paymentsService.getAllPayments();
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(payments));
  } catch (error) {
    console.error(error);
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Internal Server Error" }));
  }
};

export default {
  getAllPayments,
};
