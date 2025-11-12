import { useQuery } from "@tanstack/react-query";
import apiClient from "../client";

export interface ProductItem {
  id: number;
  name: string;
  sku?: string;
  quantity: number;
  price?: number | null;
  category?: string | null;
  image_url?: string | null;
  inventory: number;
  // otros campos opcionales que la API pudiera devolver
}

export interface ProductsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ProductItem[];
}

/**
 * useProductsQuery
 * - GET /api/products/ con params: inventory, search, category, low_stock, page, page_size
 *
 * filters: { search?, category?, low_stock?, page?, page_size? }
 */
export function useProductsQuery(
  inventoryId?: string | number,
  filters?: {
    search?: string;
    category?: string;
    low_stock?: boolean;
    page?: number;
    page_size?: number;
  },
) {
  const queryKey = ["products", inventoryId, filters];

  return useQuery<ProductsResponse>({
    queryKey,
    enabled: !!inventoryId,
    queryFn: async (): Promise<ProductsResponse> => {
      const params: Record<string, string | number> = {
        page_size: filters?.page_size ?? 20,
      };

      if (typeof inventoryId !== "undefined" && inventoryId !== null) {
        params.inventory = inventoryId;
      }

      if (filters?.search) params.search = filters.search;
      if (filters?.category) params.category = filters.category;
      if (typeof filters?.low_stock !== "undefined")
        params.low_stock = filters.low_stock ? 1 : 0;
      if (typeof filters?.page !== "undefined") params.page = filters.page;

      const { data } = await apiClient.get<ProductsResponse>("/api/products/", {
        params,
      });

      return data;
    },
    staleTime: 60 * 1000,
  });
}
