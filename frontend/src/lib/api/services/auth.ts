import apiClient from "../client";
import type { User, Tokens } from "../../store/authStore";

interface LoginResponse extends Tokens {
  user: User;
}

interface RegisterResponse {
  user: User;
  tokens: Tokens;
  message: string;
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

export async function register(
  email: string,
  password: string,
  name: string,
  plan: string = "free", // ← Default value
) {
  try {
    const response = await apiClient.post<RegisterResponse>("/api/register/", {
      email,
      password,
      name,
      plan,
    });
    return response.data;
  } catch (error) {
    console.error("Error during register:", error);
    throw error;
  }
}
