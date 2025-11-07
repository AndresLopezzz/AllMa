import apiClient from "../client";
import type { User } from "../../store/AuthStore";

interface LoginResponse {
  user: User;
  access: string;
  refresh: string;
}

interface RegisterPayload {
  email: string;
  password: string;
  password2: string;
  name: string;
  plan: "free" | "pro";
  role?: "admin" | "empleado";
}

interface RegisterResponse {
  message: string;
  token: string;
  access: string;
  refresh: string;
  user: User;
}

export async function login(email: string, password: string) {
  try {
    const response = await apiClient.post<LoginResponse>("/api/login/", {
      email,
      password,
    });

    return response.data;
  } catch (error) {
    console.error("Error during login:", error);
    throw error;
  }
}

export async function register({
  email,
  password,
  password2,
  name,
  plan,
  role = "empleado",
}: RegisterPayload) {
  try {
    const response = await apiClient.post<RegisterResponse>("/api/register/", {
      email,
      password,
      password2,
      name,
      plan,
      role,
    });

    return {
      user: response.data.user,
      access: response.data.access,
      refresh: response.data.refresh,
      message: response.data.message,
    };
  } catch (error) {
    console.error("Error during register:", error);
    throw error;
  }
}
