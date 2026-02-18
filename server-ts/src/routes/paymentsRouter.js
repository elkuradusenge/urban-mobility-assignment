import paymentsController from "../controllers/paymentsController.js";

const paymentsRouter = (req, res) => {
  const { url, method } = req;

  if (url === "/payments") {
    if (method === "GET") {
      paymentsController.getAllPayments(req, res);
      return;
    }
    if (method === "POST") {
      paymentsController.createPayment(req, res);
      return;
    }
  }

  if (url?.startsWith("/payments/")) {
    const urlParts = url.split("/");
    if (urlParts.length === 3 && urlParts[1] === "payments") {
      const id = parseInt(urlParts[2]);
      if (!isNaN(id)) {
        if (method === "GET") {
          paymentsController.getPaymentById(req, res, id);
          return;
        }
        if (method === "PUT") {
          paymentsController.updatePayment(req, res, id);
          return;
        }
        if (method === "DELETE") {
          paymentsController.deletePayment(req, res, id);
          return;
        }
      }
    }
  }
};

export default paymentsRouter;
