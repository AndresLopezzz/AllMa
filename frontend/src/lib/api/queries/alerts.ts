import { useQuery } from "@tanstack/react-query";
import apiClient from "../client";

interface AlertItem {
  id: number;
  name: string;
  sku: string;
  quantity: number;
  low_stock_threshold: number;
  price: string;
  category: string;
  image_url: string | null;
  inventory_id: number;
  inventory_name: string;
  owner_email: string;
  owner_name: string;
  criticality_ratio: number;
  alert_sent: boolean;
  stock_status: string;
  is_out_of_stock: boolean;
  created_at: string;
  updated_at: string;
}

interface AlertsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AlertItem[];
}

export function useAlertsQuery(params?: {
  new_only?: boolean;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ["alerts", params],
    queryFn: async () => {
      const { data } = await apiClient.get<AlertsResponse>("/api/alerts/", {
        params: { page_size: 10, ...params },
      });
      return data;
    },
    refetchInterval: 30_000,
  });
}

export type { AlertItem, AlertsResponse };
