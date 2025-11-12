import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "../client";

export interface InventoryItem {
  id: number;
  name: string;
  owner: number;
  template: number | null;
  template_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface InventoriesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: InventoryItem[];
}

/**
 * useInventoriesQuery
 * - GET /api/inventories/ devuelve paginado
 */
export function useInventoriesQuery(params?: { page_size?: number }) {
  return useQuery({
    queryKey: ["inventories", params],
    queryFn: async (): Promise<InventoriesResponse> => {
      const { data } = await apiClient.get<InventoriesResponse>(
        "/api/inventories/",
        {
          params: { page_size: 20, ...params },
        },
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * useCreateInventoryMutation
 * - POST /api/inventories/ con { name, template? }
 * - Invalida query ["inventories"] onSuccess
 */
export function useCreateInventoryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { name: string; template?: number | null }) => {
      const { data } = await apiClient.post("/api/inventories/", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventories"] });
    },
  });
}
