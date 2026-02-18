
export const sendResponse = (
  res,
  statusCode,
  success,
  data,
  message,
) => {
  const response = {
    success,
    data,
    message,
  };

  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(response));
};
