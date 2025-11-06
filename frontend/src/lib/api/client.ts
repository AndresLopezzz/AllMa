import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

const AUTH_FREE_ENDPOINTS = [
  "/api/login/",
  "/api/register/",
  "/api/token/",
  "/api/token/refresh/",
];

apiClient.interceptors.request.use(
  (config) => {
    const endpoint = config.url ?? "";
    const skipAuth = AUTH_FREE_ENDPOINTS.some((path) =>
      endpoint.endsWith(path),
    );

    if (!skipAuth) {
      const storedTokens = localStorage.getItem("auth-tokens");
      if (storedTokens) {
        try {
          const { access } = JSON.parse(storedTokens);
          if (access) {
            config.headers.Authorization = `Bearer ${access}`;
          } else if (config.headers.Authorization) {
            delete config.headers.Authorization;
          }
        } catch (error) {
          console.warn("Failed to parse auth tokens:", error);
          localStorage.removeItem("auth-tokens");
          localStorage.removeItem("auth-user");
        }
      } else if (config.headers.Authorization) {
        delete config.headers.Authorization;
      }
    } else if (config.headers.Authorization) {
      delete config.headers.Authorization;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

export default apiClient;
