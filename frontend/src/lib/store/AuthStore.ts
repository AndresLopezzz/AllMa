import { create } from "zustand";

export interface User {
  id: number;
  email: string;
  name: string;
  plan: "free" | "pro" | "premium";
}

export interface Tokens {
  access: string;
  refresh: string;
}

interface AuthState {
  user: User | null;
  tokens: Tokens | null;

  setUser: (user: User, tokens: Tokens) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  tokens: null,

  setUser: (user, tokens) => {
    set({ user, tokens });
    localStorage.setItem("auth-user", JSON.stringify(user));
    localStorage.setItem("auth-tokens", JSON.stringify(tokens));
  },

  isAuthenticated: () => {
    const tokens = get().tokens;
    return tokens !== null;
  },

  logout: () => {
    set({ user: null, tokens: null });
    localStorage.removeItem("auth-user");
    localStorage.removeItem("auth-tokens");
  },

  initializeAuth: () => {
    const storedUser = localStorage.getItem("auth-user");
    const storedTokens = localStorage.getItem("auth-tokens");

    if (storedUser && storedTokens) {
      try {
        const parsedUser: User = JSON.parse(storedUser);
        const parsedTokens: Tokens = JSON.parse(storedTokens);
        set({ user: parsedUser, tokens: parsedTokens });
      } catch {
        set({ user: null, tokens: null });
        localStorage.removeItem("auth-user");
        localStorage.removeItem("auth-tokens");
      }
    }
  },
}));
