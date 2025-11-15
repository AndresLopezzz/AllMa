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

// Flag para evitar loops de refresh
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });

  failedQueue = [];
};

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

// Interceptor de respuesta para manejar refresh automático
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      const endpoint = originalRequest.url ?? "";
      const isAuthEndpoint = AUTH_FREE_ENDPOINTS.some((path) =>
        endpoint.endsWith(path),
      );

      if (isAuthEndpoint) {
        // Si es endpoint de auth, no refrescar
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Si ya está refrescando, encolar la request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedTokens = localStorage.getItem("auth-tokens");
      if (storedTokens) {
        try {
          const { refresh } = JSON.parse(storedTokens);
          if (refresh) {
            // Intentar refrescar
            const refreshResponse = await apiClient.post(
              "/api/token/refresh/",
              {
                refresh,
              },
            );

            const { access: newAccess, refresh: newRefresh } =
              refreshResponse.data;

            // Guardar nuevos tokens
            localStorage.setItem(
              "auth-tokens",
              JSON.stringify({
                access: newAccess,
                refresh: newRefresh || refresh, // Si no rota, usar el mismo
              }),
            );

            // Procesar queue
            processQueue(null, newAccess);

            // Reintentar request original
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          // Refresh falló, limpiar tokens y redirigir
          localStorage.removeItem("auth-tokens");
          localStorage.removeItem("auth-user");
          processQueue(refreshError, null);
          // Redirigir a login
          window.location.href = "/login";
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // No hay refresh token, redirigir
      localStorage.removeItem("auth-tokens");
      localStorage.removeItem("auth-user");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  },
);

export default apiClient;
