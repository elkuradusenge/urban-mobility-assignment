import vendorsController from "../controllers/vendorsController.js";

const vendorsRouter = (req, res) => {
  const { url, method } = req;

  if (url === "/vendors") {
    if (method === "GET") {
      vendorsController.getAllVendors(req, res);
      return;
    }
    if (method === "POST") {
      vendorsController.createVendor(req, res);
      return;
    }
  }

  if (url?.startsWith("/vendors/")) {
    const urlParts = url.split("/");
    if (urlParts.length === 3 && urlParts[1] === "vendors") {
      const id = parseInt(urlParts[2]);
      if (!isNaN(id)) {
        if (method === "GET") {
          vendorsController.getVendorById(req, res, id);
          return;
        }
        if (method === "PUT") {
          vendorsController.updateVendor(req, res, id);
          return;
        }
        if (method === "DELETE") {
          vendorsController.deleteVendor(req, res, id);
          return;
        }
      }
    }
  }
};

export default vendorsRouter;
