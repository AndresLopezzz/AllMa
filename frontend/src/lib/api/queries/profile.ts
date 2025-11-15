import { useQuery } from "@tanstack/react-query";
import apiClient from "../client";

export interface ProfileData {
  id: number;
  name: string;
  email: string;
  plan: string; // "free", "pro", "premium"
}

/**
 * useProfileQuery
 * - GET /api/profile/
 * - Obtiene información del perfil del usuario actual
 */
export function useProfileQuery() {
  return useQuery<ProfileData>({
    queryKey: ["profile"],
    queryFn: async (): Promise<ProfileData> => {
      const { data } = await apiClient.get<ProfileData>("/api/profile/");
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}
