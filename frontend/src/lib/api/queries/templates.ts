import { useQuery } from "@tanstack/react-query";
import apiClient from "../client";

export interface TemplateField {
  name: string;
  type: string;
  required: boolean;
  options?: string[]; // opcional, solo para tipos select
}

export interface TemplateItem {
  id: number;
  name: string;
  description?: string;
  custom_fields: TemplateField[];
  created_by?: number;
  created_by_name?: string;
  created_by_email?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export function useTemplatesQuery() {
  return useQuery({
    queryKey: ["templates"],
    queryFn: async (): Promise<TemplateItem[]> => {
      const { data } = await apiClient.get("/api/templates/");
      // La API devuelve paginado con results
      return data.results ?? [];
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * useTemplateQuery
 * - GET /api/templates/{id}/
 */
export function useTemplateQuery(
  templateId: string | number,
  options?: { enabled?: boolean },
) {
  const queryKey = ["template", templateId];

  return useQuery<TemplateItem>({
    queryKey,
    enabled: !!templateId && (options?.enabled ?? true),
    queryFn: async (): Promise<TemplateItem> => {
      const { data } = await apiClient.get<TemplateItem>(
        `/api/templates/${templateId}/`,
      );

      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}
