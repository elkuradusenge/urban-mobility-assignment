import http, { IncomingMessage, ServerResponse } from "http";

const PORT = process.env.PORT || 3000;

const server = http.createServer(
  (req: IncomingMessage, res: ServerResponse) => {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("Server is running via TypeScript!");
  },
);

server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
