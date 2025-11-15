import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
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
  custom_data?: Record<string, unknown>; // campos dinámicos
  description?: string;
  low_stock_threshold?: number;
  stock_status?: string;
  is_low_stock?: boolean;
  is_out_of_stock?: boolean;
  inventory_name?: string;
  template_info?: Array<{ name: string; type: string; required: boolean }>;
  created_at?: string;
  updated_at?: string;
  // otros campos opcionales que la API pudiera devolver
}

// Tipos para crear/actualizar producto
export interface CreateProductData {
  name: string;
  sku?: string;
  description?: string;
  quantity: number;
  price?: number | null;
  low_stock_threshold?: number;
  category?: string | null;
  inventory: number;
  custom_data?: Record<string, unknown>; // campos dinámicos según template
  image?: File | null; // para FormData
}

export interface UpdateProductData
  extends Omit<CreateProductData, "inventory"> {
  id: number;
  inventory?: number; // opcional para update, para evitar mover producto accidentalmente
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

/**
 * useProductQuery
 * - GET /api/products/{id}/
 */
export function useProductQuery(
  productId: string,
  options?: { enabled?: boolean },
) {
  const queryKey = ["product", productId];

  return useQuery<ProductItem>({
    queryKey,
    enabled: !!productId && (options?.enabled ?? true),
    queryFn: async (): Promise<ProductItem> => {
      const { data } = await apiClient.get<ProductItem>(
        `/api/products/${productId}/`,
      );

      return data;
    },
    staleTime: 60 * 1000,
  });
}

/**
 * useCreateProductMutation
 * - POST /api/products/ con FormData (para incluir imagen)
 * - Invalida queries de productos al éxito
 */
export function useCreateProductMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateProductData): Promise<ProductItem> => {
      const formData = new FormData();

      // Campos estándar
      formData.append("name", data.name);
      if (data.sku) formData.append("sku", data.sku);
      if (data.description) formData.append("description", data.description);
      formData.append("quantity", data.quantity.toString());
      if (data.price != null) formData.append("price", data.price.toFixed(2));
      if (data.low_stock_threshold)
        formData.append(
          "low_stock_threshold",
          data.low_stock_threshold.toString(),
        );
      if (data.category) formData.append("category", data.category);
      formData.append("inventory", data.inventory.toString());

      // Campos dinámicos
      if (data.custom_data) {
        formData.append("custom_data", JSON.stringify(data.custom_data));
      }

      // Imagen
      if (data.image) {
        formData.append("image", data.image);
      }

      const { data: responseData } = await apiClient.post<ProductItem>(
        "/api/products/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );

      return responseData;
    },
    onMutate: async (newProduct) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["products"] });

      // Snapshot the previous value
      const previousProducts = queryClient.getQueriesData({
        queryKey: ["products"],
      });

      // Optimistically update to the new value
      queryClient.setQueriesData(
        { queryKey: ["products"] },
        (oldData: ProductsResponse | undefined) => {
          if (!oldData) return oldData;

          // For each products query, add the new product
          return {
            ...oldData,
            results: [
              {
                id: Date.now(), // Temporary ID
                ...newProduct,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                is_low_stock:
                  newProduct.quantity <= (newProduct.low_stock_threshold || 10),
                is_out_of_stock: newProduct.quantity === 0,
                stock_status:
                  newProduct.quantity === 0
                    ? "Sin stock"
                    : newProduct.quantity <=
                        (newProduct.low_stock_threshold || 10)
                      ? "Stock bajo"
                      : "En stock",
              } as ProductItem,
              ...oldData.results,
            ],
            count: oldData.count + 1,
          };
        },
      );

      // Return a context object with the snapshotted value
      return { previousProducts };
    },
    onError: (_err, _newProduct, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousProducts) {
        context.previousProducts.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}

/**
 * useUpdateProductMutation
 * - PUT /api/products/{id}/ con FormData
 * - Invalida queries de productos al éxito
 */
export function useUpdateProductMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UpdateProductData): Promise<ProductItem> => {
      const { id, ...updateData } = data;
      const formData = new FormData();

      // Campos estándar (solo si definidos)
      if (updateData.name !== undefined)
        formData.append("name", updateData.name);
      if (updateData.sku !== undefined) formData.append("sku", updateData.sku);
      if (updateData.description !== undefined)
        formData.append("description", updateData.description);
      if (updateData.quantity !== undefined)
        formData.append("quantity", updateData.quantity.toString());
      if (updateData.price != null)
        formData.append("price", updateData.price.toString());
      if (updateData.low_stock_threshold !== undefined)
        formData.append(
          "low_stock_threshold",
          updateData.low_stock_threshold.toString(),
        );
      if (updateData.category != null)
        formData.append("category", updateData.category);
      if (updateData.inventory !== undefined)
        formData.append("inventory", updateData.inventory.toString());

      // Campos dinámicos
      if (updateData.custom_data !== undefined) {
        formData.append("custom_data", JSON.stringify(updateData.custom_data));
      }

      // Imagen (si se actualiza)
      if (updateData.image !== undefined) {
        formData.append("image", updateData.image || "");
      }

      const { data: responseData } = await apiClient.patch<ProductItem>(
        `/api/products/${id}/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );

      return responseData;
    },
    onMutate: async (updatedProduct) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["products"] });

      // Snapshot the previous value
      const previousProducts = queryClient.getQueriesData({
        queryKey: ["products"],
      });

      // Optimistically update to the new value
      queryClient.setQueriesData(
        { queryKey: ["products"] },
        (oldData: ProductsResponse | undefined) => {
          if (!oldData) return oldData;

          return {
            ...oldData,
            results: oldData.results.map((product: ProductItem) =>
              product.id === updatedProduct.id
                ? {
                    ...product,
                    ...updatedProduct,
                    updated_at: new Date().toISOString(),
                    is_low_stock:
                      updatedProduct.quantity <=
                      (updatedProduct.low_stock_threshold ||
                        product.low_stock_threshold ||
                        10),
                    is_out_of_stock: updatedProduct.quantity === 0,
                    stock_status:
                      updatedProduct.quantity === 0
                        ? "Sin stock"
                        : updatedProduct.quantity <=
                            (updatedProduct.low_stock_threshold ||
                              product.low_stock_threshold ||
                              10)
                          ? "Stock bajo"
                          : "En stock",
                  }
                : product,
            ),
          };
        },
      );

      // Return a context object with the snapshotted value
      return { previousProducts };
    },
    onError: (_err, _updatedProduct, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousProducts) {
        context.previousProducts.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}

/**
 * useDeleteProductMutation
 * - DELETE /api/products/{id}/
 * - Invalida queries de productos al éxito
 */
export function useDeleteProductMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      await apiClient.delete(`/api/products/${id}/`);
    },
    onMutate: async (deletedProductId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["products"] });

      // Snapshot the previous value
      const previousProducts = queryClient.getQueriesData({
        queryKey: ["products"],
      });

      // Optimistically update to the new value
      queryClient.setQueriesData(
        { queryKey: ["products"] },
        (oldData: ProductsResponse | undefined) => {
          if (!oldData) return oldData;

          return {
            ...oldData,
            results: oldData.results.filter(
              (product: ProductItem) => product.id !== deletedProductId,
            ),
            count: oldData.count - 1,
          };
        },
      );

      // Return a context object with the snapshotted value
      return { previousProducts };
    },
    onError: (_err, _deletedProductId, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousProducts) {
        context.previousProducts.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}

/**
 * useCategoriesQuery
 * - Obtiene categorías únicas de productos en un inventario
 * - Pagina a través de todas las páginas para asegurar obtener todas las categorías
 */
export function useCategoriesQuery(inventoryId: string | number) {
  return useQuery<string[]>({
    queryKey: ["categories", inventoryId],
    enabled: !!inventoryId,
    queryFn: async (): Promise<string[]> => {
      const categories = new Set<string>();
      let nextUrl: string | null =
        `/api/products/?inventory=${inventoryId}&page_size=100`;

      while (nextUrl) {
        const response: { data: ProductsResponse } =
          await apiClient.get<ProductsResponse>(nextUrl);
        const data: ProductsResponse = response.data;
        data.results.forEach((product: ProductItem) => {
          if (product.category) categories.add(product.category);
        });
        nextUrl = data.next;
      }

      return Array.from(categories).sort();
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}
