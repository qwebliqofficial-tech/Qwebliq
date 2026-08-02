import axios from "axios";

const backendUrl = process.env.REACT_APP_BACKEND_URL;

export const api = axios.create({
  baseURL: `${backendUrl}/api`,
  withCredentials: true,
});

export function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg).filter(Boolean).join(" ");
  }
  return "Something went wrong. Please try again.";
}