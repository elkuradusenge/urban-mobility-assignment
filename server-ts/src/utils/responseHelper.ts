import { ServerResponse } from "http";

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

export const sendResponse = <T>(
  res: ServerResponse,
  statusCode: number,
  success: boolean,
  data?: T,
  message?: string,
): void => {
  const response: ApiResponse<T> = {
    success,
    data,
    message,
  };

  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(response));
};
