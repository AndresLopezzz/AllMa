import { useEffect, useState } from "react";
import { getTemplates } from "@/lib/api/services/templates";
import { Button } from "../ui/button";

export default function TemplateTest() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const templates = await getTemplates();
        setData(templates);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error desconocido");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Templates</h1>
      <Button>Prueba</Button>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
