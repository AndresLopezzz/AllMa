import apiClient from "../client";

export async function getTemplates() {
  try {
    const response = await apiClient.get("/api/templates/");
    return response.data;
  } catch (error) {
    throw error;
  }
}
