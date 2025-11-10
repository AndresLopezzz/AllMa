import { useQuery } from "@tanstack/react-query";
import apiClient from "../client";

type NumericLike = number | string;

interface DashboardInventorySummary {
  id: number;
  name: string;
}

interface DashboardCategorySummary {
  category: string;
  count: number;
}

interface DashboardValueByInventory {
  inventory_id: number;
  inventory_name: string;
  value: NumericLike;
}

interface DashboardMovement {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string;
  inventory_id: number | null;
  inventory_name: string;
  movement_type: string;
  movement_type_display: string;
  quantity: number;
  quantity_before: number;
  quantity_after: number;
  reason: string;
  performed_by: string;
  timestamp: string;
}

interface DashboardStockDistribution {
  in_stock: number;
  low_stock: number;
  out_of_stock: number;
}

interface DashboardResponse {
  total_products: number;
  total_inventory_value: NumericLike;
  low_stock_count: number;
  out_of_stock_count: number;
  total_inventories: number;
  products_by_category: DashboardCategorySummary[];
  value_by_inventory: DashboardValueByInventory[];
  recent_movements: DashboardMovement[];
  inventory?: DashboardInventorySummary | null;
}

interface DashboardData
  extends Omit<
    DashboardResponse,
    "total_inventory_value" | "value_by_inventory"
  > {
  total_value: number;
  products_by_inventory: Array<
    Omit<DashboardValueByInventory, "value"> & {
      total_value: number;
      count: number;
    }
  >;
  stock_distribution: DashboardStockDistribution;
}

export type { DashboardData, DashboardMovement };

const parseNumber = (value: NumericLike): number => {
  if (typeof value === "number") {
    return value;
  }
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const fetchDashboard = async (inventoryId?: number): Promise<DashboardData> => {
  const { data } = await apiClient.get<DashboardResponse>("/api/dashboard/", {
    params: inventoryId ? { inventory: inventoryId } : undefined,
  });

  // Calcular total_value por categoría y stock_distribution manualmente
  const products_by_inventory = data.value_by_inventory.map((item) => ({
    inventory_id: item.inventory_id,
    inventory_name: item.inventory_name,
    total_value: parseNumber(item.value),
    count: 0, // No disponible en el backend actual
  }));

  // Calcular distribución de stock basado en low_stock_count y out_of_stock_count
  const in_stock = Math.max(0, data.total_products - data.low_stock_count);

  const stock_distribution: DashboardStockDistribution = {
    in_stock: in_stock,
    low_stock: data.low_stock_count - data.out_of_stock_count,
    out_of_stock: data.out_of_stock_count,
  };

  return {
    ...data,
    total_value: parseNumber(data.total_inventory_value),
    products_by_inventory,
    stock_distribution,
  };
};

export function useDashboardQuery(inventoryId?: number) {
  return useQuery({
    queryKey: ["dashboard", { inventoryId }],
    queryFn: () => fetchDashboard(inventoryId),
    refetchInterval: 30_000,
  });
}
