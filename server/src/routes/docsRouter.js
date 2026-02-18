import fs from "fs";
import path from "path";
import swaggerSpec from "../config/swagger.js";
import { getAbsoluteFSPath } from "swagger-ui-dist";

const docsRouter = (req, res) => {
  const { url, method } = req;

  if (method !== "GET") {
    return;
  }

  // Handle redirect from /api-docs to /api-docs/
  if (url === "/api-docs") {
    res.writeHead(301, { Location: "/api-docs/" });
    res.end();
    return;
  }

  if (url === "/api-docs/swagger.json") {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(swaggerSpec));
    return;
  }

  // Serve swagger-initializer.js with custom URL
  if (url === "/api-docs/swagger-initializer.js") {
    const swaggerUiPath = getAbsoluteFSPath();
    const filePath = path.join(swaggerUiPath, "swagger-initializer.js");

    fs.readFile(filePath, "utf8", (err, data) => {
      if (err) {
        console.error("Error reading swagger-initializer.js:", err);
        res.writeHead(500);
        res.end("Error loading Swagger UI");
        return;
      }

      const updatedData = data.replace(
        "https://petstore.swagger.io/v2/swagger.json",
        "/api-docs/swagger.json"
      );

      res.setHeader("Content-Type", "application/javascript");
      res.end(updatedData);
    });
    return;
  }

  // Serve index.html at /api-docs/
  if (url === "/api-docs/") {
    const swaggerUiPath = getAbsoluteFSPath();
    const filePath = path.join(swaggerUiPath, "index.html");
    
    fs.readFile(filePath, "utf8", (err, data) => {
        if (err) {
            console.error("Error reading index.html:", err);
            res.writeHead(500);
            res.end("Error loading Swagger UI");
            return;
        }
        res.setHeader("Content-Type", "text/html");
        res.end(data);
    });
    return;
  }

  // Serve static assets
  if (url?.startsWith("/api-docs/")) {
    const filename = url.replace("/api-docs/", "");
    const swaggerUiPath = getAbsoluteFSPath();
    const filePath = path.join(swaggerUiPath, filename);

    // Security check
    if (!filePath.startsWith(swaggerUiPath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }

    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end("Not found");
        return;
      }

      const ext = path.extname(filename);
      let contentType = "text/plain";
      if (ext === ".css") contentType = "text/css";
      if (ext === ".js") contentType = "application/javascript";
      if (ext === ".png") contentType = "image/png";
      if (ext === ".html") contentType = "text/html";

      res.setHeader("Content-Type", contentType);
      res.end(data);
    });
    return;
  }
};

export default docsRouter;
