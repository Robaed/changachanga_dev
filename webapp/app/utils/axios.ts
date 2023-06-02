import type { AxiosError } from "axios";
import axios from "axios";
import type { ApiError } from "~/types";
import { BASE_API_URL } from "../config/constants";

export const api = axios.create({
  baseURL: `${BASE_API_URL}`,
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (process.env.NODE_ENV !== "production") {
      console.error(
        "Handling Error: ",
        error.status,
        error.response?.data.detail
      );
    }

    return Promise.reject(error);
  }
);

export function getApiErrorMessage(defaultMessage: string, error: unknown) {
  let message = defaultMessage;
  if (axios.isAxiosError(error)) {
    const axiosError = error.response?.data.detail;
    if (axiosError) {
      message = axiosError;
    }
  }

  return message;
}
